from fastapi import FastAPI, Query, Body,HTTPException,Depends, Response
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
import json
from sqlalchemy import create_engine,Table, MetaData, text
from sqlalchemy.orm import sessionmaker
import bcrypt
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
import datetime

app = FastAPI()


# read dataset
#df = pd.read_csv("data/combine_all3_new.csv")
load_dotenv()
DATABASE_URL=os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
metadata = MetaData()
# use SQLAlchemy read database existing table
metadata.reflect(bind=engine)
# get MySQL users table
users_table = metadata.tables["users"]

def load_data():
    query ="""
SELECT 
    c.creator_id,
    c.uniqueid,
    c.name,
    c.username,
    c.source,
    c.followers,
    c.heart,
    c.verified,
    c.country,
    c.primary_category,
    c.secondary_category,
    c.email,
    c.tier,
    c.is_brand,
    c.contact,
    c.bio,
    c.profile_url,
    c.age_children,
    c.num_children,
    c.extra_json,
    p.mentions
FROM creators c
LEFT JOIN posts p ON c.creator_id = p.creator_id;
"""

    df = pd.read_sql(query, engine)


    # expand extra_json as dynamic field
    if "extra_json" in df.columns:
        extra_series = df["extra_json"].apply(
            lambda x: json.loads(x) if isinstance(x, str) and x else {}
        )
        extra_df = pd.json_normalize(extra_series)
        df = pd.concat([df.drop(columns=["extra_json"]), extra_df], axis=1)


    # fill missing mentions
    #if "mentions" in df.columns:
        #df["mentions"] = df["mentions"].fillna(0)


    return df
#df = load_data()
   

@app.get("/influencers")
def get_influencers(
    platform: Optional[List[str]] = Query(None),
    country: Optional[List[str]] = Query(None),
    primary_category: Optional[List[str]] = Query(None),
    secondary_category: Optional[List[str]] = Query(None),
    tier: Optional[List[str]] = Query(None),
    followers_min: Optional[int] = None,
    
    is_brand: Optional[List[str]] = Query(None),
    num_children_min: Optional[int] = None,
    age_children_min:Optional[int] = None,
    
    limit: Optional[int] = None,
    skip: int = 0
):
    df= load_data()
    filtered_df = df.copy()
    filtered_df["age_children"] = pd.to_numeric(filtered_df["age_children"],errors="coerce")

    # filter by source
    if platform:
        filtered_df = filtered_df[filtered_df["source"].isin(platform)]


    # filter by country
    if country:
        filtered_df = filtered_df[filtered_df["country"].isin(country)]


    # filter by primary category
    if primary_category:
        filtered_df=filtered_df[filtered_df["primary_category"].isin(primary_category)]
    if secondary_category:
        filtered_df=filtered_df[filtered_df["secondary_category"].isin(secondary_category)]
            

    # filter by tier
    if tier:
        filtered_df = filtered_df[filtered_df["tier"].isin(tier)]

    # filter by follower number
    if followers_min is not None:
        filtered_df = filtered_df[filtered_df["followers"] >= followers_min]

    # filter by brand
    if is_brand is not None:
        filtered_df = filtered_df[filtered_df["is_brand"].isin(is_brand)]
    
    #filter by children_num
    if num_children_min is not None:
        filtered_df = filtered_df[filtered_df["num_children"]>= num_children_min]

    # filter by children_age
    if age_children_min is not None:
        filtered_df = filtered_df[filtered_df["age_children"]>= age_children_min]
    
    

    # limit of one page
    total = len(filtered_df)
    if limit is None:
        result = filtered_df.copy()
    else:
        result = filtered_df.iloc[skip: skip + limit]
    result = result.replace([np.nan,np.inf],None)

    wanted_col = [
        "creator_id","name", "username", "source", "followers", "uniqueid","heart",
        "verified", "country", "primary_category", "secondary_category","email","tier",
        "is_brand", "contact", "bio", "profile_url","age_children","num_children","mentions"
    ]
    existing_col = [c for c in wanted_col if c in result.columns]

    # JSON output
    return {
        "total":total,
        "skip":skip,
        "limit":limit,
        "items":result.to_dict(orient="records")
    }



#====Edit creators API========
@app.patch("/influencers/update-creator/{creator_id}")
def update_influencer(creator_id: int, payload: dict = Body(...)):

    allowed_fields = {
        "name", "username", "source", "followers", "uniqueid","heart","verified",
        "country", "primary_category", "secondary_category","email","tier","is_brand",
        "contact", "bio", "profile_url","age_children","num_children"
    }

    update_fields = {k: v for k, v in payload.items() if k in allowed_fields}


    if not update_fields:
        raise HTTPException(status_code=400, detail="No valid fields to update")


    # Build SQL dynamically
    set_clause = ", ".join([f"{field} = :{field}" for field in update_fields])


    sql = text(f"""
        UPDATE creators
        SET {set_clause}
        WHERE creator_id = :creator_id
    """)


    update_fields["creator_id"] = creator_id


    db = engine.connect()
    db.execute(sql, update_fields)
    db.commit()
    db.close()


    return {"status": "success", "updated": update_fields}


#========= update mentions =======
@app.patch("/influencers/update-mentions/{creator_id}")
def update_mentions_by_creator(creator_id: int, payload: dict = Body(...)):
    new_mentions = payload.get("mentions")


    if not isinstance(new_mentions, list):
        raise HTTPException(status_code=400, detail="mentions must be a list")


    sql = text("""
        UPDATE posts
        SET mentions = :mentions
        WHERE creator_id = :cid
    """)


    db = engine.connect()
    db.execute(sql, {
        "mentions": json.dumps(new_mentions),
        "cid": creator_id
    })
    db.commit()
    db.close()


    return {
        "status": "success",
        "creator_id": creator_id,
        "mentions": new_mentions
    }

#=========log in page======
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(data: LoginRequest):
    db = SessionLocal()
    user = db.execute(users_table.select().where(users_table.c.username == data.username)).first()
    db.close()


    # verify username and password
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")


    # generate JWT
    user_dict = dict(user._mapping)["password"]
    #print("DEBUG user",user)
    #print("DEBAG keys",user._mapping.keys())
    #print("DEBUG password hash from DB:", user_dict["password"])  
    #print("DEBUG type",type(user_dict.get("password")))


    if not bcrypt.checkpw(data.password.strip().encode("utf-8"), user_dict.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid username or password")


    token_data = {
        "sub": data.username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}





# ------------------ protected API ------------------
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
@app.get("/protected")
def protected(token: str= Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        return {"message": f"Hello {username}, you accessed a protected route!"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

#---------access one user to download
ALLOWED_USER = "user1"

@app.get("/influencers/export")
def export_csv(username: str):
    if username != ALLOWED_USER:
        raise HTTPException(status_code=403, detail="You are not allowed to download this file")

    df = load_data()
    return Response(
        df.to_csv(index=False),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=influencers.csv"}
    )


# ----------- Pydantic model for validation -----------
class InfluencerCreate(BaseModel):
    name: str
    username: str
    source: str
    followers: int
    uniqueid: str
    heart: int
    verified: int
    country: str
    primary_category: str
    secondary_category: str
    email: str
    tier: str
    is_brand: int
    contact: str
    bio: str
    profile_url: str
    age_children: int | None = None
    num_children: int | None = None
    


@app.post("/influencers/add-row")
def add_influencer_row(data: InfluencerCreate):
    # Connect DB
    db = engine.connect()

    try:
        insert_query = text("""
            INSERT INTO creators (
                name, username, source, followers, uniqueid, heart, verified, country,
                primary_category, secondary_category, email, tier, is_brand,
                contact, bio, profile_url, age_children, num_children
            )
            VALUES (
                :name, :username, :source, :followers, :uniqueid, :heart,
                :verified, :country, :primary_category, :secondary_category,
                :email, :tier, :is_brand, :contact, :bio, :profile_url,
                :age_children, :num_children
            );
        """)

        #db.execute(insert_query, data.dict())
        result = db.execute(insert_query,data.dict())
        db.commit()

        # get creator id
        creator_id = result.lastrowid
        if not creator_id:
            raise HTTPException(status_code=500, detail= "Failed to find creator_id")
        
        #create the post use this creator id
        insert_post_sql = text("""
            INSERT INTO posts (creator_id, mentions)
            VALUES (:cid, :mentions);
        """)


        db.execute(insert_post_sql, {
            "cid": creator_id,
            "mentions": json.dumps([])   # empty list []
        })
        db.commit()


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()

    return {"status": "success", "message": "Influencer added successfully",
            "creator_id":creator_id}


@app.post("/influencers/add-column")
def add_column(payload: dict):
    col_name = payload["column"]


    if not col_name.isidentifier():
        raise HTTPException(status_code=400, detail="Invalid column name")


    sql = text("""
        UPDATE creators
        SET extra_json = JSON_SET(
            COALESCE(extra_json, '{}'),
            :json_key,
            NULL
        );
    """)


    db = engine.connect()
    db.execute(sql, {"json_key": f"$.{col_name}"})
    db.commit()
    db.close()

    return {"status": "success", "column": col_name}


#-----save the new added column changes-------

@app.post("/influencers/save-added")
def save_dynamic(payload: dict = Body(...)):
    rows = payload["rows"]


    # original columns, not in JSON
    fixed_columns = {
        "creator_id", "uniqueid", "name", "username", "source", "followers",
        "heart", "verified", "country", "primary_category", "secondary_category",
        "email", "tier", "is_brand", "contact", "bio", "profile_url",
        "age_children", "num_children", "mentions"
    }

    
    db = engine.connect()


    for row in rows:
        creator_id = row["creator_id"]


        # extract the column in new added
        dynamic_fields = {
            k: v for k, v in row.items() if k not in fixed_columns
        }


        sql = text("""
            UPDATE creators
            SET extra_json = :json_data
            WHERE creator_id = :cid;
        """)


        db.execute(sql, {
            "json_data": json.dumps(dynamic_fields),
            "cid": creator_id
        })


    db.commit()
    db.close()


    return {"status": "success"}

