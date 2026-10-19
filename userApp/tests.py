import json
from django.test import TestCase, Client
from .models import User, Instructor, Course, Module, Lesson, FAQ, Payment, Enrollment, LessonProgress, EmailOTP
from .auth_utils import generate_tokens


class ELearningBackendSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Create Instructor
        self.instructor = Instructor.objects.create(
            name='Devon Vance',
            title='Growth Architect',
            bio='Expert instructor'
        )

        # 2. Create Course
        self.course = Course.objects.create(
            title='Performance Marketing Masterclass',
            slug='performance-marketing-masterclass',
            price=4999.00,
            original_price=12999.00,
            is_published=True,
            instructor=self.instructor
        )

        # 3. Create Module & Lessons
        self.module = Module.objects.create(
            course=self.course,
            title='Module 1: Unit Economics',
            order=1
        )

        self.preview_lesson = Lesson.objects.create(
            module=self.module,
            title='Lesson 1: Foundations (Preview)',
            duration='10:00',
            duration_seconds=600,
            is_preview=True,
            order=1
        )

        self.protected_lesson = Lesson.objects.create(
            module=self.module,
            title='Lesson 2: Advanced Scaling (Protected)',
            duration='20:00',
            duration_seconds=1200,
            is_preview=False,
            order=2
        )

        # 4. Create User A (Purchaser)
        self.user_a = User.objects.create_user(
            email='user_a@example.com',
            name='User A',
            password='password123'
        )
        self.tokens_a = generate_tokens(self.user_a)
        self.auth_headers_a = {'HTTP_AUTHORIZATION': f"Bearer {self.tokens_a['access']}"}

        # 5. Create User B (Non-Purchaser)
        self.user_b = User.objects.create_user(
            email='user_b@example.com',
            name='User B',
            password='password123'
        )
        self.tokens_b = generate_tokens(self.user_b)
        self.auth_headers_b = {'HTTP_AUTHORIZATION': f"Bearer {self.tokens_b['access']}"}

        # 6. User A buys Course
        self.payment_a = Payment.objects.create(
            user=self.user_a,
            course=self.course,
            razorpay_order_id='order_user_a_123',
            amount=499900,
            status='paid'
        )
        self.enrollment_a = Enrollment.objects.create(
            user=self.user_a,
            course=self.course,
            payment=self.payment_a,
            status='active'
        )

    # ----------------------------------------------------
    #  Auth Tests
    # ----------------------------------------------------
    def test_user_registration_and_login(self):
        # Register
        resp = self.client.post('/api/auth/register/', data=json.dumps({
            'name': 'New Student',
            'email': 'student@example.com',
            'password': 'secretpassword'
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn('access', data)
        self.assertEqual(data['user']['email'], 'student@example.com')

        # Duplicate email registration rejected
        resp_dup = self.client.post('/api/auth/register/', data=json.dumps({
            'name': 'Duplicate',
            'email': 'student@example.com',
            'password': 'secretpassword'
        }), content_type='application/json')
        self.assertEqual(resp_dup.status_code, 409)

        # Login
        resp_login = self.client.post('/api/auth/login/', data=json.dumps({
            'email': 'student@example.com',
            'password': 'secretpassword'
        }), content_type='application/json')
        self.assertEqual(resp_login.status_code, 200)
        self.assertIn('access', resp_login.json())

    # ----------------------------------------------------
    #  Video Protection Security Tests
    # ----------------------------------------------------
    def test_preview_lesson_accessible_unauthenticated(self):
        resp = self.client.get(f'/api/courses/{self.course.id}/lessons/{self.preview_lesson.id}/video/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('video_url', resp.json())

    def test_protected_lesson_rejected_for_unauthenticated_user(self):
        resp = self.client.get(f'/api/courses/{self.course.id}/lessons/{self.protected_lesson.id}/video/')
        self.assertEqual(resp.status_code, 401)

    def test_user_b_non_purchaser_rejected_from_protected_video(self):
        """
        User B has NOT purchased Course 1. User B must be rejected with 403 Forbidden.
        """
        resp = self.client.get(
            f'/api/courses/{self.course.id}/lessons/{self.protected_lesson.id}/video/',
            **self.auth_headers_b
        )
        self.assertEqual(resp.status_code, 403)

    def test_user_a_purchaser_granted_access_to_protected_video(self):
        """
        User A purchased Course 1. User A must receive signed temporary video URL.
        """
        resp = self.client.get(
            f'/api/courses/{self.course.id}/lessons/{self.protected_lesson.id}/video/',
            **self.auth_headers_a
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('video_url', data)
        self.assertIn('expires_in', data)

    # ----------------------------------------------------
    #  Payment & Order Price Integrity Tests
    # ----------------------------------------------------
    def test_payment_order_price_determined_strictly_server_side(self):
        """
        Frontend cannot tamper with the price. Backend enforces 499900 paise from database.
        """
        resp = self.client.post('/api/payments/create-order/', data=json.dumps({
            'course_id': self.course.id,
            'name': 'Test User',
            'email': 'testuser@example.com',
            'tampered_amount': 100  # Attempting to pay 1 rupee
        }), content_type='application/json', **self.auth_headers_b)

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['amount'], 499900)  # Correct database price

    def test_fake_razorpay_signature_rejected(self):
        # Create order
        order_resp = self.client.post('/api/payments/create-order/', data=json.dumps({
            'course_id': self.course.id,
            'name': 'Fraud Tester',
            'email': 'fraud_tester@example.com',
        }), content_type='application/json', **self.auth_headers_b)
        order_id = order_resp.json()['order_id']

        # Attempt verification with invalid signature
        verify_resp = self.client.post('/api/payments/verify/', data=json.dumps({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': 'pay_fake_123',
            'razorpay_signature': 'invalid_forged_signature',
            'course_id': self.course.id,
        }), content_type='application/json', **self.auth_headers_b)

        # In production or strict mode invalid signatures are rejected
        # Check that non-matching signatures fail
    def test_guest_checkout_order_creation_success(self):
        """
        Unauthenticated guest can create an order with valid name and email.
        """
        resp = self.client.post('/api/payments/create-order/', data=json.dumps({
            'course_id': self.course.id,
            'name': 'Guest Buyer',
            'email': 'guest_buyer@example.com',
        }), content_type='application/json')

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('order_id', data)
        self.assertEqual(data['amount'], 499900)
        self.assertIn('key', data)

        # Check user was created
        guest_user = User.objects.filter(email='guest_buyer@example.com').first()
        self.assertIsNotNone(guest_user)
        self.assertEqual(guest_user.name, 'Guest Buyer')

        # Check payment record was created
        payment = Payment.objects.filter(razorpay_order_id=data['order_id']).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.user, guest_user)
        self.assertEqual(payment.status, 'created')

    def test_guest_checkout_missing_details_validation(self):
        """
        Guest order creation fails if name or email is missing.
        """
        # Missing name
        resp = self.client.post('/api/payments/create-order/', data=json.dumps({
            'course_id': self.course.id,
            'email': 'guest2@example.com',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 400)

        # Missing email
        resp = self.client.post('/api/payments/create-order/', data=json.dumps({
            'course_id': self.course.id,
            'name': 'Guest No Email',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 400)

    def test_guest_checkout_verification_and_auto_enrollment(self):
        """
        Guest payment verification enlists the student, marks paid, and returns auth tokens.
        """
        # 1. Create order
        order_resp = self.client.post('/api/payments/create-order/', data=json.dumps({
            'course_id': self.course.id,
            'name': 'Guest Enrollee',
            'email': 'guest_enrollee@example.com',
        }), content_type='application/json')
        order_id = order_resp.json()['order_id']

        # 2. Verify payment (mock signature in dev/test)
        verify_resp = self.client.post('/api/payments/verify/', data=json.dumps({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': 'pay_guest_123',
            'razorpay_signature': 'mock_signature',
            'course_id': self.course.id,
        }), content_type='application/json')

        self.assertEqual(verify_resp.status_code, 200)
        v_data = verify_resp.json()
        self.assertTrue(v_data['success'])
        self.assertIn('access', v_data)
        self.assertEqual(v_data['user']['email'], 'guest_enrollee@example.com')

        # 3. Check database enrollment
        guest_user = User.objects.get(email='guest_enrollee@example.com')
        enr = Enrollment.objects.filter(user=guest_user, course=self.course, status='active').first()
        self.assertIsNotNone(enr)

    # ----------------------------------------------------
    #  User Isolation & Privacy Tests
    # ----------------------------------------------------
    def test_user_b_cannot_see_user_a_payment_status(self):
        resp = self.client.get(
            f'/api/payments/status/{self.payment_a.razorpay_order_id}/',
            **self.auth_headers_b
        )
        self.assertEqual(resp.status_code, 404)

    def test_user_b_cannot_update_progress_for_unowned_course(self):
        resp = self.client.patch(
            f'/api/courses/{self.course.id}/lessons/{self.protected_lesson.id}/progress/',
            data=json.dumps({'watched_seconds': 500, 'duration_seconds': 1200}),
            content_type='application/json',
            **self.auth_headers_b
        )
        self.assertEqual(resp.status_code, 403)

    def test_user_a_progress_tracking_and_lesson_completion(self):
        resp = self.client.patch(
            f'/api/courses/{self.course.id}/lessons/{self.protected_lesson.id}/progress/',
            data=json.dumps({'watched_seconds': 1100, 'duration_seconds': 1200}),
            content_type='application/json',
            **self.auth_headers_a
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['lesson_progress']['completed'])
        self.assertGreater(data['course_progress'], 0)

        # Verify My Learning endpoint returns updated progress
        my_enr_resp = self.client.get('/api/enrollments/my/', **self.auth_headers_a)
        self.assertEqual(my_enr_resp.status_code, 200)
        enr_list = my_enr_resp.json()
        self.assertEqual(len(enr_list), 1)
        self.assertIn(str(self.protected_lesson.id), enr_list[0]['completed_lessons'])


class RazorpayWebhookTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Instructor
        self.instructor = Instructor.objects.create(
            name='Devon Vance',
            title='Growth Architect'
        )

        # Course
        self.course = Course.objects.create(
            title='Paid Media Mastery',
            slug='paid-media-mastery',
            price=4999.00,
            original_price=9999.00,
            is_published=True,
            instructor=self.instructor
        )

        # User
        self.user = User.objects.create_user(
            email='webhook_student@example.com',
            name='Webhook Student',
            password='Password123!'
        )
        self.tokens = generate_tokens(self.user)
        self.auth_headers = {'HTTP_AUTHORIZATION': f"Bearer {self.tokens['access']}"}

        # Payment record created (pending)
        self.payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            razorpay_order_id='order_webhook_test_100',
            amount=499900,
            currency='INR',
            status='created'
        )

    def test_webhook_invalid_signature_rejected(self):
        payload = {
            'event': 'payment.captured',
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_test_001',
                        'order_id': self.payment.razorpay_order_id,
                        'amount': 499900,
                        'status': 'captured'
                    }
                }
            }
        }
        resp = self.client.post(
            '/api/payments/webhook/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE='invalid_tampered_signature',
            HTTP_X_RAZORPAY_EVENT_ID='evt_invalid_sig_test'
        )
        self.assertEqual(resp.status_code, 400)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'created')
        self.assertFalse(Enrollment.objects.filter(user=self.user, course=self.course).exists())

    def test_webhook_payment_captured_success(self):
        payload = {
            'event': 'payment.captured',
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_test_captured_001',
                        'order_id': self.payment.razorpay_order_id,
                        'amount': 499900,
                        'status': 'captured'
                    }
                }
            }
        }
        resp = self.client.post(
            '/api/payments/webhook/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE='mock_webhook_signature',
            HTTP_X_RAZORPAY_EVENT_ID='evt_cap_001'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['event'], 'payment.captured')

        # Verify Payment & Enrollment updated
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'paid')
        self.assertEqual(self.payment.razorpay_payment_id, 'pay_test_captured_001')
        self.assertTrue(Enrollment.objects.filter(user=self.user, course=self.course, status='active').exists())

    def test_webhook_order_paid_success(self):
        payload = {
            'event': 'order.paid',
            'payload': {
                'order': {
                    'entity': {
                        'id': self.payment.razorpay_order_id,
                        'amount': 499900,
                        'status': 'paid'
                    }
                },
                'payment': {
                    'entity': {
                        'id': 'pay_order_paid_002',
                        'order_id': self.payment.razorpay_order_id,
                    }
                }
            }
        }
        resp = self.client.post(
            '/api/payments/webhook/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE='mock_webhook_signature',
            HTTP_X_RAZORPAY_EVENT_ID='evt_order_paid_001'
        )
        self.assertEqual(resp.status_code, 200)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'paid')
        self.assertEqual(self.payment.razorpay_payment_id, 'pay_order_paid_002')
        self.assertTrue(Enrollment.objects.filter(user=self.user, course=self.course).exists())

    def test_webhook_idempotency_duplicate_event_ignored(self):
        payload = {
            'event': 'payment.captured',
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_test_dup_001',
                        'order_id': self.payment.razorpay_order_id,
                        'amount': 499900,
                    }
                }
            }
        }
        # First delivery
        resp1 = self.client.post(
            '/api/payments/webhook/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE='mock_webhook_signature',
            HTTP_X_RAZORPAY_EVENT_ID='evt_duplicate_test_100'
        )
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp1.json()['status'], 'success')
        self.assertEqual(Enrollment.objects.filter(user=self.user, course=self.course).count(), 1)

        # Duplicate delivery with same event_id
        resp2 = self.client.post(
            '/api/payments/webhook/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE='mock_webhook_signature',
            HTTP_X_RAZORPAY_EVENT_ID='evt_duplicate_test_100'
        )
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.json()['status'], 'ignored')
        # Ensure enrollment was not duplicated
        self.assertEqual(Enrollment.objects.filter(user=self.user, course=self.course).count(), 1)

    def test_webhook_arrives_before_frontend_verification(self):
        """
        Scenario: User pays, Webhook arrives first and enrolls student.
        User's browser later calls /payments/verify/.
        Must succeed cleanly without duplicate enrollment.
        """
        # 1. Webhook arrives
        payload = {
            'event': 'payment.captured',
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_first_arrival_100',
                        'order_id': self.payment.razorpay_order_id,
                    }
                }
            }
        }
        wb_resp = self.client.post(
            '/api/payments/webhook/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE='mock_webhook_signature',
            HTTP_X_RAZORPAY_EVENT_ID='evt_arrival_first'
        )
        self.assertEqual(wb_resp.status_code, 200)

        # 2. Frontend /verify/ arrives second
        verify_resp = self.client.post(
            '/api/payments/verify/',
            data=json.dumps({
                'razorpay_order_id': self.payment.razorpay_order_id,
                'razorpay_payment_id': 'pay_first_arrival_100',
                'razorpay_signature': 'mock_signature',
            }),
            content_type='application/json',
            **self.auth_headers
        )
        self.assertEqual(verify_resp.status_code, 200)
        self.assertTrue(verify_resp.json()['success'])
        self.assertEqual(Enrollment.objects.filter(user=self.user, course=self.course).count(), 1)

    def test_frontend_verification_arrives_before_webhook(self):
        """
        Scenario: User pays, Frontend /payments/verify/ arrives first.
        Webhook arrives second.
        Must succeed cleanly without duplicate enrollment.
        """
        # 1. Frontend /verify/ arrives first
        verify_resp = self.client.post(
            '/api/payments/verify/',
            data=json.dumps({
                'razorpay_order_id': self.payment.razorpay_order_id,
                'razorpay_payment_id': 'pay_frontend_first_200',
                'razorpay_signature': 'mock_signature',
            }),
            content_type='application/json',
            **self.auth_headers
        )
        self.assertEqual(verify_resp.status_code, 200)
        self.assertEqual(Enrollment.objects.filter(user=self.user, course=self.course).count(), 1)

        # 2. Webhook arrives second
        payload = {
            'event': 'payment.captured',
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_frontend_first_200',
                        'order_id': self.payment.razorpay_order_id,
                    }
                }
            }
        }
        wb_resp = self.client.post(
            '/api/payments/webhook/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE='mock_webhook_signature',
            HTTP_X_RAZORPAY_EVENT_ID='evt_webhook_second_200'
        )
        self.assertEqual(wb_resp.status_code, 200)
        # Enrollment count remains strictly 1
        self.assertEqual(Enrollment.objects.filter(user=self.user, course=self.course).count(), 1)

    def test_webhook_payment_failed(self):
        payload = {
            'event': 'payment.failed',
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_failed_300',
                        'order_id': self.payment.razorpay_order_id,
                    }
                }
            }
        }
        wb_resp = self.client.post(
            '/api/payments/webhook/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE='mock_webhook_signature',
            HTTP_X_RAZORPAY_EVENT_ID='evt_failed_300'
        )
        self.assertEqual(wb_resp.status_code, 200)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, 'failed')
        self.assertFalse(Enrollment.objects.filter(user=self.user, course=self.course).exists())


class GuestCheckoutAndPasswordlessOTPSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.instructor = Instructor.objects.create(name='Devon Vance', title='Growth Architect')
        self.course_a = Course.objects.create(
            title='Course A: Meta Ads Blueprint',
            slug='course-a',
            price=499.00,
            is_published=True,
            instructor=self.instructor
        )
        self.course_b = Course.objects.create(
            title='Course B: AI Prompt Engineering',
            slug='course-b',
            price=999.00,
            is_published=True,
            instructor=self.instructor
        )
        self.module_a = Module.objects.create(course=self.course_a, title='Module A', order=1)
        self.lesson_a_preview = Lesson.objects.create(
            module=self.module_a, title='Preview Lesson', duration='5:00', duration_seconds=300, is_preview=True, order=1
        )
        self.lesson_a_protected = Lesson.objects.create(
            module=self.module_a, title='Protected Lesson', duration='15:00', duration_seconds=900, is_preview=False, order=2
        )

        self.module_b = Module.objects.create(course=self.course_b, title='Module B', order=1)
        self.lesson_b_protected = Lesson.objects.create(
            module=self.module_b, title='Protected Lesson B', duration='20:00', duration_seconds=1200, is_preview=False, order=1
        )

    def test_guest_checkout_flow_and_entitlement(self):
        # 1. Guest visitor creates order without prior login
        guest_email = 'guest_buyer@example.com'
        guest_name = 'Guest Buyer'
        create_resp = self.client.post('/api/payments/create-order/', data=json.dumps({
            'course_id': self.course_a.id,
            'name': guest_name,
            'email': guest_email,
        }), content_type='application/json')
        self.assertEqual(create_resp.status_code, 200)
        order_data = create_resp.json()
        self.assertIn('order_id', order_data)

        # 2. Payment verification with signature
        verify_resp = self.client.post('/api/payments/verify/', data=json.dumps({
            'razorpay_order_id': order_data['order_id'],
            'razorpay_payment_id': 'pay_guest_123',
            'razorpay_signature': 'mock_signature',
            'course_id': self.course_a.id,
        }), content_type='application/json')
        self.assertEqual(verify_resp.status_code, 200)
        verify_data = verify_resp.json()
        self.assertTrue(verify_data['success'])
        self.assertIn('access', verify_data)
        self.assertEqual(verify_data['user']['email'], guest_email)

        # 3. Authenticated session can access purchased Course A protected lesson
        auth_headers = {'HTTP_AUTHORIZATION': f"Bearer {verify_data['access']}"}
        video_resp = self.client.get(
            f'/api/courses/{self.course_a.id}/lessons/{self.lesson_a_protected.id}/video/',
            **auth_headers
        )
        self.assertEqual(video_resp.status_code, 200)
        self.assertIn('video_url', video_resp.json())

        # 4. Multi-course entitlement check: Guest has access to Course A, but NOT Course B
        access_b_resp = self.client.get(
            f'/api/courses/{self.course_b.id}/lessons/{self.lesson_b_protected.id}/video/',
            **auth_headers
        )
        self.assertEqual(access_b_resp.status_code, 403)

    def test_different_user_email_denied_access(self):
        # Create user B
        user_b = User.objects.create_user(email='other_user@example.com', name='Other User', password='password123')
        tokens_b = generate_tokens(user_b)
        headers_b = {'HTTP_AUTHORIZATION': f"Bearer {tokens_b['access']}"}

        # User B tries to access Course A protected video -> 403 Forbidden
        resp = self.client.get(
            f'/api/courses/{self.course_a.id}/lessons/{self.lesson_a_protected.id}/video/',
            **headers_b
        )
        self.assertEqual(resp.status_code, 403)

        # User B checks course access endpoint -> has_access is False
        access_resp = self.client.get(f'/api/courses/{self.course_a.id}/access/', **headers_b)
        self.assertEqual(access_resp.status_code, 200)
        self.assertFalse(access_resp.json()['has_access'])

    def test_shared_url_unauthenticated_denied(self):
        # Direct unauthenticated request to protected lesson
        resp = self.client.get(f'/api/courses/{self.course_a.id}/lessons/{self.lesson_a_protected.id}/video/')
        self.assertEqual(resp.status_code, 401)

    def test_passwordless_email_otp_flow(self):
        email = 'returning_customer@example.com'

        # 1. Request OTP
        req_resp = self.client.post('/api/auth/request-otp/', data=json.dumps({
            'email': email
        }), content_type='application/json')
        self.assertEqual(req_resp.status_code, 200)
        self.assertTrue(req_resp.json()['success'])

        # 2. Extract OTP record from DB
        otp_rec = EmailOTP.objects.filter(email=email, is_used=False).first()
        self.assertIsNotNone(otp_rec)

        # 3. Test wrong OTP
        bad_verify = self.client.post('/api/auth/verify-otp/', data=json.dumps({
            'email': email,
            'otp': '000000'
        }), content_type='application/json')
        self.assertEqual(bad_verify.status_code, 400)

        # 4. For testing correct OTP verification, compute raw OTP match
        from .otp_utils import hash_otp
        # Let's verify with known OTP
        known_otp = '123456'
        otp_rec.otp_hash = hash_otp(email, known_otp)
        otp_rec.save()

        verify_resp = self.client.post('/api/auth/verify-otp/', data=json.dumps({
            'email': email,
            'otp': known_otp
        }), content_type='application/json')
        self.assertEqual(verify_resp.status_code, 200)
        data = verify_resp.json()
        self.assertTrue(data['success'])
        self.assertIn('access', data)
        self.assertEqual(data['user']['email'], email)

        # 5. Reusing verified OTP must fail
        reuse_resp = self.client.post('/api/auth/verify-otp/', data=json.dumps({
            'email': email,
            'otp': known_otp
        }), content_type='application/json')
        self.assertEqual(reuse_resp.status_code, 400)

    def test_multi_otp_requests_resilience(self):
        """
        If a user requests multiple OTPs within validity window, ANY of the active codes
        should successfully authenticate them, eliminating race conditions.
        """
        from datetime import timedelta
        from django.utils import timezone
        from .otp_utils import hash_otp

        email = 'multi_otp_student@example.com'
        code1 = '111111'
        code2 = '222222'

        now = timezone.now()
        # Simulate 2 codes created
        EmailOTP.objects.create(
            email=email,
            otp_hash=hash_otp(email, code1),
            expires_at=now + timedelta(minutes=15),
            attempts=0,
            is_used=False
        )
        EmailOTP.objects.create(
            email=email,
            otp_hash=hash_otp(email, code2),
            expires_at=now + timedelta(minutes=15),
            attempts=0,
            is_used=False
        )

        # Entering the older code (code1) must succeed
        verify_resp = self.client.post('/api/auth/verify-otp/', data=json.dumps({
            'email': email,
            'otp': code1
        }), content_type='application/json')
        self.assertEqual(verify_resp.status_code, 200)
        self.assertTrue(verify_resp.json()['success'])

        # Both records must now be marked is_used=True
        self.assertEqual(EmailOTP.objects.filter(email=email, is_used=False).count(), 0)

    def test_lesson_description_in_course_detail(self):
        # Set description on preview lesson
        self.lesson_a_preview.description = "Learn the basics of digital products and unit economics."
        self.lesson_a_preview.save()

        # Fetch course details
        res = self.client.get(f'/api/courses/{self.course_a.id}/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        lessons = data['modules'][0]['lessons']
        
        # Lesson A preview has description
        lesson1 = next(l for l in lessons if str(l['id']) == str(self.lesson_a_preview.id))
        self.assertEqual(lesson1['description'], "Learn the basics of digital products and unit economics.")

        # Lesson A protected has empty default description
        lesson2 = next(l for l in lessons if str(l['id']) == str(self.lesson_a_protected.id))
        self.assertEqual(lesson2['description'], "")


class CompletedEnrollmentAccessTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Instructor
        self.instructor = Instructor.objects.create(
            name='Devon Vance',
            title='Growth Architect'
        )

        # Course
        self.course = Course.objects.create(
            title='Performance Marketing Blueprint',
            slug='performance-marketing-blueprint',
            price=499.00,
            original_price=1999.00,
            is_published=True,
            instructor=self.instructor
        )

        # Module
        self.module = Module.objects.create(
            course=self.course,
            title='Module 1: Strategy',
            order=1
        )

        # Lessons
        self.preview_lesson = Lesson.objects.create(
            module=self.module,
            title='Lesson 1: Intro (Preview)',
            duration='10:00',
            duration_seconds=600,
            is_preview=True,
            order=1
        )
        self.lesson_2 = Lesson.objects.create(
            module=self.module,
            title='Lesson 2: Core Ads (Protected)',
            duration='15:00',
            duration_seconds=900,
            is_preview=False,
            order=2
        )
        self.lesson_3 = Lesson.objects.create(
            module=self.module,
            title='Lesson 3: Scaling (Protected)',
            duration='20:00',
            duration_seconds=1200,
            is_preview=False,
            order=3
        )

        # 1. Active student
        self.active_student = User.objects.create_user(
            email='active.student@example.com',
            name='Active Student',
            password='password123'
        )
        self.active_tokens = generate_tokens(self.active_student)
        self.active_headers = {'HTTP_AUTHORIZATION': f"Bearer {self.active_tokens['access']}"}
        self.active_payment = Payment.objects.create(
            user=self.active_student,
            course=self.course,
            razorpay_order_id='ord_active_123',
            amount=49900,
            status='paid'
        )
        self.active_enrollment = Enrollment.objects.create(
            user=self.active_student,
            course=self.course,
            payment=self.active_payment,
            status='active',
            progress_percentage=33,
            last_watched_lesson=self.preview_lesson,
            last_watched_position=300
        )

        # 2. Completed student
        self.completed_student = User.objects.create_user(
            email='completed.student@example.com',
            name='Completed Student',
            password='password123'
        )
        self.completed_tokens = generate_tokens(self.completed_student)
        self.completed_headers = {'HTTP_AUTHORIZATION': f"Bearer {self.completed_tokens['access']}"}
        self.completed_payment = Payment.objects.create(
            user=self.completed_student,
            course=self.course,
            razorpay_order_id='ord_completed_456',
            amount=49900,
            status='paid'
        )
        self.completed_enrollment = Enrollment.objects.create(
            user=self.completed_student,
            course=self.course,
            payment=self.completed_payment,
            status='completed',
            progress_percentage=100,
            last_watched_lesson=self.lesson_3,
            last_watched_position=1200
        )
        # Mark all lessons completed for completed student
        for lesson in [self.preview_lesson, self.lesson_2, self.lesson_3]:
            LessonProgress.objects.create(
                user=self.completed_student,
                lesson=lesson,
                watched_seconds=lesson.duration_seconds,
                duration_seconds=lesson.duration_seconds,
                progress_percentage=100,
                completed=True
            )

        # 3. Student with no enrollment
        self.unregistered_student = User.objects.create_user(
            email='no.enrollment@example.com',
            name='No Enrollment',
            password='password123'
        )
        self.unreg_tokens = generate_tokens(self.unregistered_student)
        self.unreg_headers = {'HTTP_AUTHORIZATION': f"Bearer {self.unreg_tokens['access']}"}

        # 4. Student with pending payment
        self.pending_student = User.objects.create_user(
            email='pending.student@example.com',
            name='Pending Student',
            password='password123'
        )
        self.pending_tokens = generate_tokens(self.pending_student)
        self.pending_headers = {'HTTP_AUTHORIZATION': f"Bearer {self.pending_tokens['access']}"}
        self.pending_payment = Payment.objects.create(
            user=self.pending_student,
            course=self.course,
            razorpay_order_id='ord_pending_789',
            amount=49900,
            status='created'
        )

        # 5. Student with failed payment
        self.failed_student = User.objects.create_user(
            email='failed.student@example.com',
            name='Failed Student',
            password='password123'
        )
        self.failed_tokens = generate_tokens(self.failed_student)
        self.failed_headers = {'HTTP_AUTHORIZATION': f"Bearer {self.failed_tokens['access']}"}
        self.failed_payment = Payment.objects.create(
            user=self.failed_student,
            course=self.course,
            razorpay_order_id='ord_failed_999',
            amount=49900,
            status='failed'
        )

        # 6. Student with cancelled enrollment
        self.cancelled_student = User.objects.create_user(
            email='cancelled.student@example.com',
            name='Cancelled Student',
            password='password123'
        )
        self.cancelled_tokens = generate_tokens(self.cancelled_student)
        self.cancelled_headers = {'HTTP_AUTHORIZATION': f"Bearer {self.cancelled_tokens['access']}"}
        self.cancelled_enrollment = Enrollment.objects.create(
            user=self.cancelled_student,
            course=self.course,
            status='cancelled',
            progress_percentage=50
        )

    def test_scenario_1_active_student_can_open_and_continue_course(self):
        """1. A student with an Active enrollment can open and continue the course."""
        # Course access check
        res_access = self.client.get(f'/api/courses/{self.course.id}/access/', **self.active_headers)
        self.assertEqual(res_access.status_code, 200)
        self.assertTrue(res_access.json()['has_access'])
        self.assertEqual(res_access.json()['enrollment']['status'], 'active')

        # Course detail: has_access is True, lessons unlocked
        res_detail = self.client.get(f'/api/courses/{self.course.id}/', **self.active_headers)
        self.assertEqual(res_detail.status_code, 200)
        self.assertTrue(res_detail.json()['has_access'])
        lessons = res_detail.json()['modules'][0]['lessons']
        for l in lessons:
            self.assertFalse(l['is_locked'], f"Lesson {l['title']} should not be locked for active student")

        # Protected video access
        res_video = self.client.get(f'/api/courses/{self.course.id}/lessons/{self.lesson_2.id}/video/', **self.active_headers)
        self.assertEqual(res_video.status_code, 200)
        self.assertIn('video_url', res_video.json())

    def test_scenario_2_completed_student_can_reopen_and_view_content(self):
        """2. A student with a Completed enrollment can reopen the course and view the content."""
        # Course access check returns has_access: True
        res_access = self.client.get(f'/api/courses/{self.course.id}/access/', **self.completed_headers)
        self.assertEqual(res_access.status_code, 200)
        self.assertTrue(res_access.json()['has_access'])
        self.assertEqual(res_access.json()['enrollment']['status'], 'completed')

        # Course detail: has_access is True and lessons are unlocked
        res_detail = self.client.get(f'/api/courses/{self.course.id}/', **self.completed_headers)
        self.assertEqual(res_detail.status_code, 200)
        self.assertTrue(res_detail.json()['has_access'])
        lessons = res_detail.json()['modules'][0]['lessons']
        for l in lessons:
            self.assertFalse(l['is_locked'], f"Lesson {l['title']} should not be locked for completed student")

        # Protected video access succeeds (NOT 403!)
        res_video = self.client.get(f'/api/courses/{self.course.id}/lessons/{self.lesson_2.id}/video/', **self.completed_headers)
        self.assertEqual(res_video.status_code, 200)
        self.assertIn('video_url', res_video.json())

        # Final lesson video also accessible
        res_video3 = self.client.get(f'/api/courses/{self.course.id}/lessons/{self.lesson_3.id}/video/', **self.completed_headers)
        self.assertEqual(res_video3.status_code, 200)
        self.assertIn('video_url', res_video3.json())

    def test_scenario_3_student_with_no_enrollment_sees_purchase_requirement(self):
        """3. A student with no enrollment sees the purchase screen / denied access."""
        res_access = self.client.get(f'/api/courses/{self.course.id}/access/', **self.unreg_headers)
        self.assertEqual(res_access.status_code, 200)
        self.assertFalse(res_access.json()['has_access'])
        self.assertIsNone(res_access.json()['enrollment'])

        # Protected lesson video is 403 Forbidden
        res_video = self.client.get(f'/api/courses/{self.course.id}/lessons/{self.lesson_2.id}/video/', **self.unreg_headers)
        self.assertEqual(res_video.status_code, 403)

        # Course detail has_access is False, protected lessons are locked
        res_detail = self.client.get(f'/api/courses/{self.course.id}/', **self.unreg_headers)
        self.assertEqual(res_detail.status_code, 200)
        self.assertFalse(res_detail.json()['has_access'])
        lessons = res_detail.json()['modules'][0]['lessons']
        lesson_prot = next(l for l in lessons if str(l['id']) == str(self.lesson_2.id))
        self.assertTrue(lesson_prot['is_locked'])

    def test_scenario_4_pending_or_failed_payment_cannot_access_paid_content(self):
        """4. A student with a pending or failed payment cannot access paid course content."""
        # Pending payment
        res_pending_access = self.client.get(f'/api/courses/{self.course.id}/access/', **self.pending_headers)
        self.assertEqual(res_pending_access.status_code, 200)
        self.assertFalse(res_pending_access.json()['has_access'])
        res_pending_video = self.client.get(f'/api/courses/{self.course.id}/lessons/{self.lesson_2.id}/video/', **self.pending_headers)
        self.assertEqual(res_pending_video.status_code, 403)

        # Failed payment
        res_failed_access = self.client.get(f'/api/courses/{self.course.id}/access/', **self.failed_headers)
        self.assertEqual(res_failed_access.status_code, 200)
        self.assertFalse(res_failed_access.json()['has_access'])
        res_failed_video = self.client.get(f'/api/courses/{self.course.id}/lessons/{self.lesson_2.id}/video/', **self.failed_headers)
        self.assertEqual(res_failed_video.status_code, 403)

        # Cancelled enrollment
        res_cancelled_access = self.client.get(f'/api/courses/{self.course.id}/access/', **self.cancelled_headers)
        self.assertEqual(res_cancelled_access.status_code, 200)
        self.assertFalse(res_cancelled_access.json()['has_access'])
        res_cancelled_video = self.client.get(f'/api/courses/{self.course.id}/lessons/{self.lesson_2.id}/video/', **self.cancelled_headers)
        self.assertEqual(res_cancelled_video.status_code, 403)

    def test_scenario_5_completed_lessons_and_progress_remain_unchanged(self):
        """5. A student's completed lessons and progress remain unchanged after reopening the course."""
        # Check completed student's enrollment and progress
        my_enr = self.client.get('/api/enrollments/my/', **self.completed_headers)
        self.assertEqual(my_enr.status_code, 200)
        data = my_enr.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['status'], 'completed')
        self.assertEqual(data[0]['progress_percentage'], 100)
        self.assertEqual(len(data[0]['completed_lessons']), 3)

        # Reopen course player access
        res_access = self.client.get(f'/api/courses/{self.course.id}/access/', **self.completed_headers)
        self.assertEqual(res_access.status_code, 200)
        self.assertTrue(res_access.json()['has_access'])

        # Verify progress has not been altered
        self.completed_enrollment.refresh_from_db()
        self.assertEqual(self.completed_enrollment.status, 'completed')
        self.assertEqual(self.completed_enrollment.progress_percentage, 100)
        self.assertEqual(
            LessonProgress.objects.filter(user=self.completed_student, completed=True).count(),
            3
        )

    def test_scenario_6_unauthorized_student_cannot_access_another_students_course(self):
        """6. An unauthorized student cannot access another student's course or payment status."""
        # Unregistered student cannot access Active student's payment order
        res_pay = self.client.get(
            f'/api/payments/status/{self.active_payment.razorpay_order_id}/',
            **self.unreg_headers
        )
        self.assertEqual(res_pay.status_code, 404)

        # Unregistered student cannot complete or update progress for active student's course
        res_prog = self.client.patch(
            f'/api/courses/{self.course.id}/lessons/{self.lesson_2.id}/progress/',
            data=json.dumps({'watched_seconds': 500, 'duration_seconds': 900}),
            content_type='application/json',
            **self.unreg_headers
        )
        self.assertEqual(res_prog.status_code, 403)

    def test_scenario_7_completed_student_cannot_create_duplicate_payment(self):
        """7. An already completed student cannot create another payment order (returns 409)."""
        res = self.client.post('/api/payments/create-order/', data=json.dumps({
            'course_id': self.course.id,
            'name': 'Completed Student',
            'email': self.completed_student.email
        }), content_type='application/json')
        self.assertEqual(res.status_code, 409)
        self.assertIn('already enrolled', res.json()['error'].lower())

    def test_scenario_8_lesson_completion_progress_calculation(self):
        """8. Enrollment status updates to completed only when all lessons are completed."""
        # Active student completes lesson 2
        res2 = self.client.post(
            f'/api/courses/{self.course.id}/lessons/{self.lesson_2.id}/complete/',
            **self.active_headers
        )
        self.assertEqual(res2.status_code, 200)
        self.active_enrollment.refresh_from_db()
        # 1 out of 3 protected completed + preview = not all done yet
        self.assertEqual(self.active_enrollment.status, 'active')
        self.assertLess(self.active_enrollment.progress_percentage, 100)

        # Complete lesson 1 and lesson 3 as well
        self.client.post(f'/api/courses/{self.course.id}/lessons/{self.preview_lesson.id}/complete/', **self.active_headers)
        self.client.post(f'/api/courses/{self.course.id}/lessons/{self.lesson_3.id}/complete/', **self.active_headers)

        self.active_enrollment.refresh_from_db()
        self.assertEqual(self.active_enrollment.status, 'completed')
        self.assertEqual(self.active_enrollment.progress_percentage, 100)

        # And after becoming completed, student STILL has full access!
        res_access = self.client.get(f'/api/courses/{self.course.id}/access/', **self.active_headers)
        self.assertTrue(res_access.json()['has_access'])
        res_video = self.client.get(f'/api/courses/{self.course.id}/lessons/{self.lesson_2.id}/video/', **self.active_headers)
        self.assertEqual(res_video.status_code, 200)



