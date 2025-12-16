import pandas as pd
import re
#! pip install pandas sqlalchemy pymysql
from sqlalchemy import create_engine


# MySQL connection
engine = create_engine()


def clean_hashtag(tag: str) -> str:
    if not tag or not isinstance(tag, str):
        return None


    tag = tag.strip()                    
    tag = tag.lower()                     
    tag = re.sub(r"[^a-z0-9_]+", "", tag) 

    if len(tag) < 2:
        return None

    if len(tag) > 50:
        return None


    # remove 2 digit number ("06", "18")
    if re.fullmatch(r"\d{2}", tag):
        return None

    return tag


def main():
    # read hashtag from sql
    df = pd.read_sql("SELECT hashtag FROM unique_hashtags", engine)

    df["clean_tag"] = df["hashtag"].apply(clean_hashtag)


    df = df.dropna(subset=["clean_tag"])
    df = df.drop_duplicates(subset=["clean_tag"])

    df_clean = df[["clean_tag"]].rename(columns={"clean_tag": "hashtag"})
    df_clean.to_sql("unique_hashtags", engine, if_exists="replace", index=False)
    print(f"✅ successfully clean and write back")



if __name__ == "__main__":
    main()
