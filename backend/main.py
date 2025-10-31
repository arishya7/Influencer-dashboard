from fastapi import FastAPI, Query, Body,HTTPException,Depends
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
from sqlalchemy import create_engine,Table, MetaData
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
    p.mentions
FROM creators c
LEFT JOIN posts p ON c.creator_id = p.creator_id;
"""
    return pd.read_sql(query,engine)
df = load_data()

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
        "name", "username", "source", "followers", "uniqueid","heart","verified",
        "country", "primary_category", "secondary_category","email","tier","is_brand",
        "contact", "bio", "profile_url","age_children","num_children","mentions"
    ]
    existing_col = [c for c in wanted_col if c in result.columns]

    # JSON output
    return {
        "total":total,
        "skip":skip,
        "limit":limit,
        "items":result[existing_col].to_dict(orient="records")
    }



#====Edit API========
@app.patch("/influencers/{uniqueid}")
def update_influencer(uniqueid: str, updates: dict = Body(...)):
    global df

    if uniqueid not in df["uniqueid"].values:
        raise HTTPException(status_code=404, detail="not found")

    idx = df.index[df["uniqueid"].astype(str) == str(uniqueid)][0]

    for field, value in updates.items():
        if field in df.columns:   
            df.at[idx, field] = value

    #df.to_csv("data/combine_all3_new.csv", index=False)
    df_creators = df.drop(columns=["mentions"])
    df_creators.to_sql("creators",engine,if_exists="append",index=False)
    record = df.loc[idx].replace([np.nan,np.inf],None).to_dict()
    return {"status": "success", 
            "update_fields":updates,
            "id":uniqueid,
            "data": record}

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
