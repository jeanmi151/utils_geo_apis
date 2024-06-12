import json
import requests
import re
import urllib3
import sys

# adding local file
from meta_manipulation import Meta_manipulation


# disable https checks (for testing or development server)
# urllib3.disable_warnings()


class Ask_gn_api:
    def __init__(self, server, username, password ):
        self.server = server
        self.username = username
        self.password = password
        self.xsrf_token = ""
        self.session = requests.Session()

    # put this right before function
    def generate_xsfr(self):

        authenticate_url = self.server + '/geonetwork/srv/fre/info?type=me'

        # To generate the XRSF token, send a post request to the following URL: http://localhost:8080/geonetwork/srv/eng/info?type=me
        response = self.session.post(authenticate_url)

        # Extract XRSF token
        self.xsrf_token = response.cookies.get("XSRF-TOKEN")
        if self.xsrf_token:
            print("The XSRF Token is:", self.xsrf_token)
        else:
            print(response.text)
            print("Unable to find the XSRF token")

    # possible value for uuidprocessing : NOTHING , OVERWRITE , GENERATEUUID
    def upload_metadata(self, metadata, groupid='100', uuidprocessing='GENERATEUUID', publish=False):
        headers = {'Accept': 'application/json',
                   'X-XSRF-TOKEN': self.xsrf_token,
        }

        # Set the parameters
        params = {
            'metadataType': 'METADATA',
            'uuidProcessing': uuidprocessing,
            'transformWith': '_none_',
            'group': groupid,
            'publishToAll': str(publish).lower()
        }

        # session = requests.Session()

        # print(username, password, xsrf_token, server, params, headers)
        # Send a put request to the endpoint
        response = self.session.post( self.server + '/geonetwork/srv/api/records',
         json=params,
         params=params,
         auth = (self.username, self.password),
         headers=headers,
         files={'file': metadata}
         )


        if response.status_code == 200 or response.status_code == 201 :
            answer_api = json.loads(response.text)
            print("Upload metadatahere : " + self.server + "/geonetwork/srv/fre/catalog.search#/metadata/" +
                   answer_api['metadataInfos'][list(answer_api['metadataInfos'])[0]][0]['uuid'])
            # print(answer_api)
            return answer_api
        elif response.status_code == 400:
            answer_api = json.loads(response.text)
            print(answer_api)
            return False
        else:
            print(response)
            print(response.text)
            return False

    # not working yet
    def upload_thesaurus_dict(self, filename):
        headers = {
                   'Accept': 'application/json',
                  'X-XSRF-TOKEN': self.xsrf_token,
                   'Origin': 'http://localhost',
                   'Referer': 'http://localhost/geonetwork/srv/fre/admin.console',
        } #

        # Set the parameters
        params = {
            '_csrf': self.xsrf_token,
            'url': '',
            'registryUrl' : '',
            'registryType': '',
            'type': 'local',
            'dir': 'theme',
        } #  'stylesheet': '_none_',

        cookies = {
            'XSRF-TOKEN':self.xsrf_token,
        }
        response = self.session.post( self.server + '/geonetwork/srv/api/registries/vocabularies?_csrf='+self.xsrf_token,
                                      auth=(self.username, self.password),
                                     headers=headers, cookies=cookies, data=params,
                                     files=[('file', (filename, open(filename,'rb').read(), 'application/rdf+xml'))]
                                     )
        req = response.request
        print('{}\n{}\r\n{}\r\n\r\n{}'.format(
            '-----------START-----------',
            req.method + ' ' + req.url,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            req.body,
        ))
        print(response.request)
        print("uploaded new thesaurus")
        print(response)
        print(response.text)

    def closesession(self):
        self.session.close()


if __name__ == "__main__":
    file_to_update = sys.argv[1]

    print("Will upload the file " + file_to_update)

    # Set up your username and password:
    username = 'admin'
    password = 'admin'

    # Set up your server and the authentication URL:
    server = "http://localhost"
    final_server = "http://localhost"

    api_obj = Ask_gn_api(server=server, username=username, password=password)

    f = open(file_to_update)
    meta_to_upload = f.read()
    f.close()

    meta_to_upload_updated = Meta_manipulation.add_thesaurus(meta_to_upload, title="Category",
                                                         server=final_server, thesaurus_value="test1",
                                                         local_thesaurus_name="exemple"
                                                         )
    api_obj.generate_xsfr()
    # api_obj.upload_thesaurus_dict("exemple.rdf")
    api_obj.upload_metadata(metadata=meta_to_upload_updated, uuidprocessing="OVERWRITE", publish=True)

    api_obj.closesession()
