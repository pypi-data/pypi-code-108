import os, requests, json, logging, glob
from google.cloud import storage
from .utils import Utils
from .models.product import Product
from .models.order import Order
from .models.order_item import OrderItem


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")
server_url = 'https://connection.nappsolutions.io'
google_service_account = {
    "type": "service_account",
    "project_id": "napp-storage-prd",
    "private_key_id": "94bfd544589144cb5468f18112cb177481662bb9",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCtNBr5AV5NXmiB\nmqIgE5xkzUXJN3++VFNfHBFUK330O+BopYKHUZqS44LsOWOMSL/dHY/OIht1LKvi\niqsN/AamSruk/P80LQWlukfDr/opoaZxNiLwhb0CornRGWQZVZb0Y+iN3/3/qCz6\noa9QdXw9pfBLPopQaKVN9pNHtdtyppipJaezNnBCn1l5iYCNSq3mPXgxq9ApjNd2\nJE3pCmEfGdgkWGFGZquYu8MExvO52AX0OE4tk913V8lSi5lHeBVxLqxQQpFDZqII\n79wD2t6uxGj6sQgjKakg+LMFjig5BGf40quK7PPXfc30RozXYZPDQAfgby/CfPUl\nQAIbBk7TAgMBAAECggEABzoR2ArxEtxaEvJPSnRXBbO08jjhGSFumxzSMkdgSYUI\nD4W8ZQYII5HfoBii6TMN4l195xVwPNrgzyKHEZ3O7zhWDQPLaDNqtWgI34bjssH+\nbmHaYlvKL6Z3h1x+WzpBgq/6f5T1hanQOqLtbDeCuBXI6XLSFZnQL+kWaxsQ7X8p\nSBmzoRnR/e/jW9J7V6J1536epJEc/p7yXUsxcbFJXiKTSeONQ8/3mCXwJeE5sGHa\nl+eXc8XDw4QoqbHxoAa+MKIW/oJYbAHY2FzIIMrOH81LieIUhw/alL8EhgjHAtGK\nQJPF27jtSujwQYv//bJMNb+nt8xsbuyw8wmP73xqJQKBgQDyH4Z74Xm/8sYgfqyF\nNLewyFRDMbMq/21FVh5VMHI/4utc8zQy9KdBu7qexsY0miBBKL+PnAdCwOnSDT7Z\nqZpcf11n18G7cTu8HwWqthsYAbHbJX3hox6uMtO9dHnv9Rn1qEICbQb5IpH7J95O\nBIzCiLdSIgAEU4+GlxjbxZDWnwKBgQC3IWEIox6m4Q/qOh4UAOs4eaepQbbfU5oS\ndCJcz15oiHBxUYxdMCnp1D+CuGvLAN3Ts+jFvjtXDAESGylUqQThribeprgTn36n\nW15fx0W0jQQC4ttkLnckoMJmgz34LKWVXSeIccD/oxCxkLOO2VuLDqO41m8l4JGa\nlNh3QzefTQKBgFfHtioThOBiVBJT2pgwlKgy+NmjmyFrmWIZ5sVb2w/uZQY95h7T\nNBBQz0fhKNrJRghZjZmzJ6674gmVY8PmCWCfjG2pe0NJui5p0NQjUY9Sjfi1jv3O\n9cCSDNIS+GJWqiK17biTboPEVMiJm78NRzr/9faA/SCUauSQwyJqbihhAoGBAIjf\nmt3QxX0nJDUFwStkUGrCiqy34A3lN3fpczF5EHAC4j/gGpAgCoOpTtrOKkrtV97+\nTdFWUJXL9BTrViXfujVPa9/oLhcEk65UXSIrF49OApyBoEatcAFhYksqdqvB+vS7\nTmvt0bl/0F9W7s2q6X/yri3dn+9ofItUCsKA69bVAoGADwrV0W6ZZZ1euaUyBvzG\nFdKGr6GO/xvSlOxn4wT8udtnyY8CG9bscI3vdZk4LVw0gdf5la+mNC9kjkSslbin\nSW1NEzCqSWNaJyCE3AtpWF+vt1KSpqwm/fOmtDwhREVrckofQBYmrU+t09bHuqSQ\n/zf6iIiFOSD9IWrJPdglBqQ=\n-----END PRIVATE KEY-----\n",
    "client_email": "nappclient-prd@napp-storage-prd.iam.gserviceaccount.com",
    "client_id": "104414236656478786142",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/nappclient-prd%40napp-storage-prd.iam.gserviceaccount.com"
}
key_path = f'./service-account.json'


class NappClient2Controller:
    @classmethod
    def get_integration(self, store_reference):
        if store_reference:
            headers = dict()
            headers['Authorization'] = 'Basic YWRtaW5AbmFwcHNvbHV0aW9ucy5jb206bmFwcDE1NDg3OA=='
            r = requests.get(f'{server_url}/integration/store_id/{store_reference}', headers=headers)
            return json.loads(r.content.decode('utf-8'))
        else:
            logging.info('[NappClient2] Invalid store reference to get integration')
            return None


    @classmethod
    def create_event(self, status, event, stacktrace=None, total_orders=None, bucket=None):
        headers = dict()
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'Basic YWRtaW5AbmFwcHNvbHV0aW9ucy5jb206bmFwcDE1NDg3OA=='
        
        payload = dict()
        payload['status'] = f'{status}'
        payload['file'] = f'{event}'
        payload['stacktrace'] = stacktrace 
        payload['total_orders'] = total_orders
        payload['bucket'] = bucket
        
        if status and event:
            response = requests.post(f'{server_url}/event/history', headers=headers, data=json.dumps(payload))
            logging.info(f"[NappClient2] Creating event {event} with status '{status}' - {response.status_code} {payload}")
        else:
            logging.info('[NappClient2] Invalid status or event, error to create event')
            return None
        
    
    @classmethod
    def save_files(self, output_path = '', products: Product = [], orders: Order = [], order_items: OrderItem = [], revision: int = 1, version: int = 1):
        csvs = glob.glob(f'{output_path}/*.csv')
        zips = glob.glob(f'{output_path}/*.zip')
        
        try:
            for file in csvs:
                os.remove(file)
        except:
            pass

        try:
            for file in zips:
                os.remove(file)
        except:
            pass
        
        if len(products) > 0:
            Utils.create_csv(f'{output_path}/product_r{revision}_v{version}.csv', products)
        if len(orders) > 0:
            Utils.create_csv(f'{output_path}/order_r{revision}_v{version}.csv', orders)
        if len(order_items) > 0:
            Utils.create_csv(f'{output_path}/order_item_r{revision}_v{version}.csv', order_items)


    @classmethod
    def upload_file(self, store_reference, bucket, output_path):
        try:
            # create storage account key
            if not os.path.exists(key_path):
                with open(key_path, 'w') as key_file:
                    json.dump(google_service_account, key_file)
            
            # create storage account
            storage_client = storage.Client.from_service_account_json(key_path)

            # blob config
            filename = Utils.create_zip(output_path)
            event = f"{store_reference}/{filename.split('/')[-1]}"
            bucket_obj = storage_client.bucket(bucket)
            blob = bucket_obj.blob(event)
            blob.upload_from_filename(filename)
            logging.info(f'[NappClient2] Upload file {filename} with success')

            # remove storage account file
            os.remove(key_path)
        except Exception as e:
            logging.error(f'[NappClient2] Error to upload file: {e}')


    @classmethod
    def upload_storage_file(self, store_reference, bucket, file, folder=None):
        try:
            # create storage account key
            if not os.path.exists(key_path):
                with open(key_path, 'w') as key_file:
                    json.dump(google_service_account, key_file)
            
            # create storage account
            storage_client = storage.Client.from_service_account_json(key_path)

            # blob config
            event = f"{store_reference}/{file.split('/')[-1]}"
            if folder:
                event = f"{store_reference}/{folder}/{file.split('/')[-1]}"

            bucket_obj = storage_client.bucket(bucket)
            blob = bucket_obj.blob(event)
            blob.upload_from_filename(file)
            logging.info(f'[NappClient2] Upload file {file} with success')
            
            # remove storage account file
            os.remove(key_path)
        except Exception as e:
            logging.error(f'[NappClient2] Error to upload file: {e}')


    @classmethod
    def download_storage_file(self, store_reference, bucket, file):
        try:
            # create storage account key
            if not os.path.exists(key_path):
                with open(key_path, 'w') as key_file:
                    json.dump(google_service_account, key_file)
            
            # create storage account
            storage_client = storage.Client.from_service_account_json(key_path)

            # blob configs
            event = f"{store_reference}/{file.split('/')[-1]}"
            bucket_obj = storage_client.bucket(bucket)
            blob = bucket_obj.blob(event)
            blob.download_to_filename(file)
            logging.info(f'[NappClient2] Download file {file} with success')

            # remove storage account file
            os.remove(key_path)

        except Exception as e:
            logging.info(f'[NappClient2] Error to downlaod file: {e}')
