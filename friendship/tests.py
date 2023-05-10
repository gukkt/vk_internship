from rest_framework.test import APITestCase

from friendship.services import is_friends, request_exists


class FriendshipTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        usernames = ['Вася', 'Петя', 'Коля', 'Саша', 'Маша', 'Даша', 'Глаша', 'Паша', 'Миша', 'Гоша', 'Катя', 'Лена']
        for username in usernames:
            self.client.post('/api/users/', data={'username': username})

    def test_friendship_create(self):
        data = {
            'from_user': 1,
            'to_user': 2,
        }
        response = self.client.post(f'/api/friendships/requests/{data["from_user"]}-{data["to_user"]}/send_request/')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(request_exists(data['from_user'], data['to_user']), True)
        response = self.client.post(f'/api/friendships/requests/{data["from_user"]}-{data["to_user"]}/send_request/')
        self.assertEqual(response.status_code, 409)
        self.assertEqual(is_friends(data['from_user'], data['to_user']), False)

    def test_friendship_create_cross(self):
        data = {
            'from_user': 5,
            'to_user': 3,
        }
        response = self.client.post(f'/api/friendships/requests/{data["from_user"]}-{data["to_user"]}/send_request/')
        self.assertEqual(response.status_code, 201)
        response = self.client.post(f'/api/friendships/requests/{data["to_user"]}-{data["from_user"]}/send_request/')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'You have successfully sent the request. '
                                                   'Since you already have a request from this user, you automatically become friends.')
        self.assertEqual(is_friends(data['from_user'], data['to_user']), True)
        self.assertEqual(request_exists(data['to_user'], data['from_user']), False)

    def test_friendship_create_invalid(self):
        data = {
            'from_user': 1,
            'to_user': 999,
        }
        response = self.client.post(f'/api/friendships/requests/{data["from_user"]}-{data["to_user"]}/send_request/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(request_exists(data['from_user'], data['to_user']), False)
        self.assertEqual(is_friends(data['from_user'], data['to_user']), False)

    def test_friendship_accept_request(self):
        data = {
            'from_user': 1,
            'to_user': 2,
        }
        response = self.client.post(f'/api/friendships/requests/{data["from_user"]}-{data["to_user"]}/send_request/')
        self.assertEqual(response.status_code, 201)
        response = self.client.post(f'/api/friendships/requests/{data["to_user"]}-{data["from_user"]}/accept_request/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(is_friends(data['from_user'], data['to_user']), True)
        self.assertEqual(request_exists(data['from_user'], data['to_user']), False)

    def test_friendship_accept_request_by_sender(self):
        data = {
            'from_user': 1,
            'to_user': 2,
        }
        response = self.client.post(f'/api/friendships/requests/{data["from_user"]}-{data["to_user"]}/send_request/')
        self.assertEqual(response.status_code, 201)
        response = self.client.post(f'/api/friendships/requests/{data["from_user"]}-{data["to_user"]}/accept_request/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(is_friends(data['from_user'], data['to_user']), False)
        self.assertEqual(request_exists(data['from_user'], data['to_user']), True)

    def test_friendship_accept_request_invalid(self):
        data = {
            'from_user': 7,
            'to_user': 2,
        }
        response = self.client.post(f'/api/friendships/requests/{data["to_user"]}-{data["from_user"]}/accept_request/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(is_friends(data['from_user'], data['to_user']), False)
        self.assertEqual(request_exists(data['from_user'], data['to_user']), False)

    def test_friendship_reject_request(self):
        data = {
            'from_user': 1,
            'to_user': 4,
        }
        response = self.client.post(f'/api/friendships/requests/{data["from_user"]}-{data["to_user"]}/send_request/')
        self.assertEqual(response.status_code, 201)
        response = self.client.post(f'/api/friendships/requests/{data["to_user"]}-{data["from_user"]}/decline_request/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(is_friends(data['from_user'], data['to_user']), False)
        self.assertEqual(request_exists(data['from_user'], data['to_user']), False)
