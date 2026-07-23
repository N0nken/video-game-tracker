from requests import post
response = post('https://api.igdb.com/v4/genres', **{'headers': {'Client-ID': 'i1czz7rk9c505lscvmtw5civw39toy', 'Authorization': 'Bearer access_token'},'data': 'fields checksum,created_at,name,slug,updated_at,url;'})
print ("response: %s" % str(response.json()))

secret = c6073w27inbt3dw4r75zgih32cilcq