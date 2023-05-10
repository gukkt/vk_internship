from rest_framework.test import APITestCase


class UserTestCase(APITestCase):
    def test_user_create(self):
        data = {
            'username': 'Вася',
        }
        response = self.client.post('/api/users/', data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['username'], 'Вася')

    def test_user_create_invalid(self):
        data = {
            'username': '',
        }
        response = self.client.post('/api/users/', data=data)
        self.assertEqual(response.status_code, 400)

    def test_user_detail(self):
        data = {
            'username': 'Вася',
        }
        response = self.client.post('/api/users/', data=data)
        self.assertEqual(response.status_code, 201)
        user_id = response.data['id']
        response = self.client.get(f'/api/users/{user_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'Вася')

    def test_user_detail_invalid(self):
        response = self.client.get('/api/users/999/')
        self.assertEqual(response.status_code, 404)
