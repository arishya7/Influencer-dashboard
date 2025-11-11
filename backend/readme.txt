run the following:
uvicorn backend.main:app --reload

API key, method:GET
http://127.0.0.1:8000/influencers


# parameter name in API 
http://127.0.0.1:8000/influencers?platform=  ,possible value is [Instragram, Tiktok, Rednote]
http://127.0.0.1:8000/influencers?country=
http://127.0.0.1:8000/influencers?primary_category=..&secondary_category=..
http://127.0.0.1:8000/influencers?tier= ,possible value is['Micro', 'Macro', 'Nano', 'Celebrity', 'Seeder']
http://127.0.0.1:8000/influencers?followers_min=
http://127.0.0.1:8000/influencers?is_brand=     ,possible_value is['Unknown', 'Influencer', 'Brand']
http://127.0.0.1:8000/influencers?num_children_min
http://127.0.0.1:8000/influencers?age_children_min=
http://127.0.0.1:8000/influencers?limit=
category dictionary
primary_category:{
    "Parenting + Lifestyle": "Parenting%20%2B%20Lifestyle",
    "General Audience Brands": "General%20Audience%20Brands",
    "Parenting + Beauty & Fashion": "Parenting%20%2B%20Beauty%20%26%20Fashion",
    "Core Parenting & Family": "Core%20Parenting%20%26%20Family",
    "Parenting + Travel": "Parenting%20%2B%20Travel",
    "Mompreneurs / Dadpreneurs": "Mompreneurs%20%2F%20Dadpreneurs",
    "Family-Focused Brands & Services": "Family-Focused%20Brands%20%26%20Services",
    "Parenting + Food": "Parenting%20%2B%20Food",
    "Parenting + Health & Wellness": "Parenting%20%2B%20Health%20%26%20Wellness"
}
secondary_category: {
    "Lifestyle Mom / Dad": "Lifestyle%20Mom%20%2F%20Dad",
    "General Business": "General%20Business",
    "Mom Style / Beauty": "Mom%20Style%20%2F%20Beauty",
    "Mom / Dad Blogger": "Mom%20%2F%20Dad%20Blogger",
    "Home & Living Family Blogger": "Home%20%26%20Living%20Family%20Blogger",
    "Family Travel Blogger": "Family%20Travel%20Blogger",
    "Parenting Expert": "Parenting%20Expert",
    "Professional Services": "Professional%20Services",
    "Baby / Kids’ Products": "Baby%20%2F%20Kids%E2%80%99%20Products",
    "Family Food Blogger": "Family%20Food%20Blogger",
    "Founder / Entrepreneur": "Founder%20%2F%20Entrepreneur",
    "Family Fitness & Health": "Family%20Fitness%20%26%20Health",
    "General Lifestyle / Brand": "General%20Lifestyle%20%2F%20Brand",
    "Baby / Kids' Products": "Baby%20%2F%20Kids%27%20Products",
    "Family Vlog / Activities": "Family%20Vlog%20%2F%20Activities"
}

=======Edit and save change API of creators =============
http://localhost:8000/influencers/update-creator/2736
method: PATCH
parameter:creator_id (2736)
body, json
{"num_children":2}

====== Edit and save change of mentions =====
http://localhost:8000/influencers/update-mentions/2736
method: PATCH
parameter:creator_id(2736)
body, json
{
  "mentions": ["mummys market"]
}

===== login ===
http://localhost:8000/login 
method: POST

==== export csv for main user ======
http://localhost:8000/influencers/export
method: GET 
parameter: user1

==== add new row ===
http://localhost:8000/influencers/add-row
method: POST 
{
  "name": "string",
  "username": "string",
  "source": "string",
  "followers": 0,
  "uniqueid": "string",
  "heart": 0,
  "verified": 0,
  "country": "string",
  "primary_category": "string",
  "secondary_category": "string",
  "email": "string",
  "tier": "string",
  "is_brand": 0,
  "contact": "string",
  "bio": "string",
  "profile_url": "string",
  "age_children": 0,
  "num_children": 0
}

====== add new column ====
http://localhost:8000/influencers/add-column
method: POST 
{
  "column": "outbound_status"
}

==== save the change of new columns =====
http://localhost:8000/influencers/save-added
method:POST 
{
  "row": [
    {
        "creator_id":2377,
        "outbound_status":"sent"
    }
  ]
}