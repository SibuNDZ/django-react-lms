"""Profile avatars and course thumbnails always resolve to a usable image URL."""

from rest_framework import status

from core.test_views import BaseAPITestCase


class MediaFallbackTests(BaseAPITestCase):

    def test_profile_without_upload_gets_default_avatar_url(self):
        self.authenticate_as_student()
        response = self.client.get('/api/v1/user/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        image = response.data['image']
        self.assertTrue(image.startswith('http'), image)
        self.assertTrue(image.endswith('/static/img/default-avatar.svg'), image)

    def test_course_without_thumbnail_gets_placeholder_url(self):
        response = self.client.get('/api/v1/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = response.data.get('results', response.data)
        self.assertTrue(items)
        thumb = items[0]['thumbnail']
        self.assertTrue(thumb.startswith('http'), thumb)
        self.assertTrue(thumb.endswith('/static/img/course-placeholder.svg'), thumb)

        response = self.client.get(f'/api/v1/courses/{self.course.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['thumbnail'].endswith('/static/img/course-placeholder.svg'))
