import httpx
import json
import os
import time
from app.core.config import settings


class ProspecRepository:
    def __init__(self):
        self.base_url = settings.api_prospec_base_url
        self.username = settings.api_prospec_username
        self.password = settings.api_prospec_password
        self.token = None

    async def authenticate(self) -> str:
        """Authenticate and get token"""
        url = f"{self.base_url}/api/Token"
        
        headers = {
            'content-type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'password',
            'username': self.username,
            'password': self.password
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            response.raise_for_status()
            token_json = response.json()
            self.token = token_json["access_token"]
            return self.token

    async def _get_headers(self) -> dict:
        """Get headers with authentication token"""
        if not self.token:
            await self.authenticate()
        
        return {
            'Authorization': f'Bearer {self.token}',
            "Content-Type": "application/json"
        }

    async def _handle_auth_error(self, response):
        """Handle 401 authentication errors"""
        if response.status_code == 401:
            await self.authenticate()
            return True
        return False

    async def get_studies_by_tag(self, tags: dict) -> dict:
        """Get studies filtered by tags"""
        url = f"{self.base_url}/api/v2/prospectiveStudies/"
        headers = await self._get_headers()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=tags)
            
            if await self._handle_auth_error(response):
                headers = await self._get_headers()
                response = await client.get(url, headers=headers, params=tags)
            
            response.raise_for_status()
            return response.json()

    async def get_estudo_por_id(self, id_estudo: str) -> dict:
        """Get information about a specific study"""
        url = f"{self.base_url}/api/prospectiveStudies/{id_estudo}"
        headers = await self._get_headers()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if await self._handle_auth_error(response):
                headers = await self._get_headers()
                response = await client.get(url, headers=headers)
            
            response.raise_for_status()
            return response.json()

    async def get_status_estudo(self, id_estudo: str) -> str:
        """Get status of a specific study"""
        study_info = await self.get_estudo_por_id(id_estudo)
        return study_info['Status']

    async def duplicate_study(self, id_estudo: str, title: str, description: str, tags: list, 
                            vazoes_dat: int = 2, vazoes_rvx: int = 1, prevs_condition: int = 1) -> str:
        """Duplicate an existing study"""
        url = f"{self.base_url}/api/prospectiveStudies/{id_estudo}/Duplicate"
        headers = await self._get_headers()
        
        list_of_tags = []
        for tag in tags:
            tag_config = {
                'Text': tag[0],
                'TextColor': tag[1],
                'BackgroundColor': tag[2]
            }
            list_of_tags.append(tag_config)
        
        data = {
            "Title": title,
            "Description": description,
            "Tags": list_of_tags,
            "VazoesDatCondition": vazoes_dat,
            "VazoesRvxCondition": vazoes_rvx,
            "PrevsCondition": prevs_condition
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=json.dumps(data))
            
            if await self._handle_auth_error(response):
                headers = await self._get_headers()
                response = await client.post(url, headers=headers, data=json.dumps(data))
            
            response.raise_for_status()
            return response.text.strip('"')

    async def run_execution(self, id_estudo: str, execution_config: dict) -> None:
        """Start study execution"""
        url = f"{self.base_url}/api/prospectiveStudies/{id_estudo}/Run"
        headers = await self._get_headers()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=json.dumps(execution_config))
            
            if await self._handle_auth_error(response):
                headers = await self._get_headers()
                response = await client.post(url, headers=headers, data=json.dumps(execution_config))
            
            response.raise_for_status()

    async def download_compilation(self, id_estudo: str, file_path: str) -> None:
        """Download study compilation"""
        url = f"{self.base_url}/api/prospectiveStudies/{id_estudo}/CompilationDownload"
        headers = await self._get_headers()
        
        async with httpx.AsyncClient() as client:
            async with client.stream('POST', url, headers=headers) as response:
                if await self._handle_auth_error(response):
                    headers = await self._get_headers()
                    async with client.stream('POST', url, headers=headers) as response:
                        response.raise_for_status()
                        with open(file_path, 'wb') as f:
                            async for chunk in response.aiter_bytes():
                                f.write(chunk)
                else:
                    response.raise_for_status()
                    with open(file_path, 'wb') as f:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)

    async def send_file_to_deck(self, id_estudo: str, deck_id: str, file_path: str, file_name: str) -> None:
        """Send file to a specific deck"""
        url = f"{self.base_url}/api/prospectiveStudies/{id_estudo}/UploadFiles?deckId={deck_id}"
        
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        
        async with httpx.AsyncClient() as client:
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f, 'multipart/form-data')}
                response = await client.post(url, headers=headers, files=files)
                
                if await self._handle_auth_error(response):
                    headers['Authorization'] = f'Bearer {self.token}'
                    with open(file_path, 'rb') as f:
                        files = {'file': (file_name, f, 'multipart/form-data')}
                        response = await client.post(url, headers=headers, files=files)
                
                response.raise_for_status()

    async def associate_cuts(self, id_estudo: str, associations: list) -> None:
        """Associate cuts between studies"""
        url = f"{self.base_url}/api/prospectiveStudies/{id_estudo}/Associate"
        headers = await self._get_headers()
        
        data = {
            "cortesAssociation": associations
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=json.dumps(data))
            
            if await self._handle_auth_error(response):
                headers = await self._get_headers()
                response = await client.post(url, headers=headers, data=json.dumps(data))
            
            response.raise_for_status()

    async def associate_volumes(self, id_estudo: str, associations: list) -> None:
        """Associate volumes between studies"""
        url = f"{self.base_url}/api/prospectiveStudies/{id_estudo}/Associate"
        headers = await self._get_headers()
        
        data = {
            "volumeAssociation": associations
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=json.dumps(data))
            
            if await self._handle_auth_error(response):
                headers = await self._get_headers()
                response = await client.post(url, headers=headers, data=json.dumps(data))
            
            response.raise_for_status()

    async def remove_study_tags(self, id_estudo: str, tags_to_remove: list) -> None:
        url = f"{self.base_url}/api/prospectiveStudies/{id_estudo}/RemoveTags"
        headers = await self._get_headers()
        
        data = {
            "tags": tags_to_remove
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=headers, data=json.dumps(data))
            
            if await self._handle_auth_error(response):
                headers = await self._get_headers()
                response = await client.patch(url, headers=headers, data=json.dumps(data))
            
            response.raise_for_status()
            return response.json()

            
    async def add_study_tags(self, id_estudo: str, tags_to_add: list) -> None:
        url = f"{self.base_url}/api/prospectiveStudies/{id_estudo}/AddTags"
        headers = await self._get_headers()
        
        data = {
            "tags": tags_to_add
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=json.dumps(data))
            
            if await self._handle_auth_error(response):
                headers = await self._get_headers()
                response = await client.post(url, headers=headers, data=json.dumps(data))
            
            response.raise_for_status()
            return response.json()


    async def update_estudos(self, id_estudo: str, id_deck: str, filename: str, file_bytes: bytes) -> dict:
        url = f'{self.base_url}/api/prospectiveStudies/{id_estudo}/UploadFiles'
        headers = await self._get_headers()
        params = {'deckId': id_deck}
        files = {
            "file": (filename, file_bytes, 'multipart/form-data', {'Expires': '0'})
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, params=params, files=files)
        if await self._handle_auth_error(response):
            headers = await self._get_headers()
            response = await client.post(url, headers=headers, params=params, files=files)
        response.raise_for_status()
        return response.json()
