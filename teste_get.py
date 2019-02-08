import urllib.request
import shutil
url = "https://storage.googleapis.com/softinova_executivaadm/sources/SEFIP_ARAUCO.pdf"
output_file = "name.pdf"
with urllib.request.urlopen(url) as response, open(output_file, 'wb') as out_file:
     shutil.copyfileobj(response, out_file)