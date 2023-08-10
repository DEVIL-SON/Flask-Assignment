import unittest
import requests
import random

class TestYourFlaskApp(unittest.TestCase):

    def setUp(self):
        self.url = "http://127.0.0.1:5000"
        self.user_name = f"test_user_{random.randint(1, int(1e6))}"
        self.key_name = f"test_key_{random.randint(1, int(1e6))}"

    def test_register_user(self):
        endpoint = "/api/register"
        data = {
            "username": self.user_name,
            "email": f"{self.user_name}@example.com",
            "password": "test_password",
            "full_name": "Test User",
            "age": 30,
            "gender": "male"
        }
        response = requests.post(self.url + endpoint, json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "User successfully registered!")

    def test_generate_token(self):
        endpoint = "/api/token"
        data = {
            "username": self.user_name,
            "password": "test_password"
        }
        response = requests.post(self.url + endpoint, json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Access token generated successfully.")
        self.auth_header = {"Authorization": f"Bearer {response.json()['data']['access_token']}"}

    def test_store_data(self):
        endpoint = "/api/data"
        data = {
            "key": self.key_name,
            "value": "test_value"
        }
        response = requests.post(self.url + endpoint, json=data, headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Data stored successfully.")

    def test_retrieve_data(self):
        endpoint = f"/api/data/{self.key_name}"
        response = requests.get(self.url + endpoint, headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["key"], self.key_name)
        self.assertEqual(response.json()["data"]["value"], "test_value")

    def test_update_data(self):
        endpoint = f"/api/data/{self.key_name}"
        data = {
            "value": "new_test_value"
        }
        response = requests.put(self.url + endpoint, json=data, headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Data updated successfully.")

    def test_delete_data(self):
        endpoint = f"/api/data/{self.key_name}"
        response = requests.delete(self.url + endpoint, headers=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Data deleted successfully.")

if __name__ == "__main__":
    unittest.main()
