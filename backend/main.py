from fastapi import FastAPI, Query
from typing import List, Optional
import pandas as pd
import numpy as np


app = FastAPI()


# read dataset
df = pd.read_csv("data/combine_all3_new.csv")


@app.get("/influencers")
def get_influencers(
    platform: Optional[List[str]] = Query(None),
    country: Optional[List[str]] = Query(None),
    primary_category: Optional[List[str]] = Query(None),
    secondary_category: Optional[List[str]] = Query(None),
    tier: Optional[List[str]] = Query(None),
    followers_min: Optional[int] = None,
    
    is_brand: Optional[bool] = None,
    num_children_min: Optional[int] = None,
    age_children_min:Optional[int] = None,
    
    limit: int = 50,
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
        filtered_df = filtered_df[filtered_df["is_brand"]==is_brand]
    
    #filter by children_num
    if num_children_min is not None:
        filtered_df = filtered_df[filtered_df["num_children"]>= num_children_min]

    # filter by children_age
    if age_children_min is not None:
        filtered_df = filtered_df[filtered_df["age_children"]>= age_children_min]
    
    

    # limit of one page
    total = len(filtered_df)
    result = filtered_df.iloc[skip: skip + limit]
    result = result.replace([np.nan,np.inf],None)

    wanted_col = [
        "name", "username", "source", "followers", "uniqueid","heart","verified",
        "country", "primary_category", "secondary_category","email","tier",
        "contact", "bio", "profile_url","age_children","mentions"
    ]
    existing_col = [c for c in wanted_col if c in result.columns]

    # JSON output
    return {
        "total":total,
        "skip":skip,
        "limit":limit,
        "items":result[existing_col].to_dict(orient="records")
    }
