import requests

def fetch_info():
  res = requests.get("http://pi.hole/admin/api.php")
  if res.status_code == 200:
    return res.json()