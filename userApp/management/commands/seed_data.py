from typing import List, TypedDict
from django.core.management.base import BaseCommand
from django.db import transaction
from userApp.models import User, Instructor, Course, Module, Lesson, FAQ, Enrollment, Payment


class LessonData(TypedDict):
    title: str
    description: str
    duration: str
    duration_seconds: int
    is_preview: bool
    order: int
    video_url: str


class ModuleData(TypedDict):
    title: str
    order: int
    lessons: List[LessonData]


class Command(BaseCommand):
    help = 'Seeds complete sample masterclasses, instructors, modules, lessons, FAQs, and demo user data.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding sample courses and platform data...')

        with transaction.atomic():
            # =========================================================
            # 1. Instructors
            # =========================================================
            instructor_ai, _ = Instructor.objects.get_or_create(
                name='AI Digital Product Academy',
                defaults={
                    'title': 'Digital Entrepreneur & AI Creator',
                    'bio': 'Helping creators, professionals, and freelancers monetize their knowledge and launch profitable digital assets.',
                    'avatar': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&q=80',
                }
            )

            instructor_devon, _ = Instructor.objects.get_or_create(
                name='Devon Vance',
                defaults={
                    'title': 'Principal Paid Media Buyer & Growth Architect',
                    'bio': 'Managed over $25M+ in profitable ad spend across DTC eCommerce and digital products. Creator of the Dynamic Creative Testing Engine.',
                    'avatar': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80',
                }
            )

            instructor_marcus, _ = Instructor.objects.get_or_create(
                name='Marcus Chen',
                defaults={
                    'title': 'AI Systems Architect & Full-Stack Engineer',
                    'bio': 'Ex-Google AI Engineer, founder of two SaaS ventures. Specializes in building production LLM pipelines, autonomous agents, and Next.js platforms.',
                    'avatar': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&q=80',
                }
            )

            instructor_sarah, _ = Instructor.objects.get_or_create(
                name='Sarah Jenkins',
                defaults={
                    'title': 'High-Ticket Agency Founder & Sales Strategist',
                    'bio': 'Scaled 3 B2B service agencies from 0 to 7-figures using systematic cold outreach, automated inbound funnels, and high-converting offer structures.',
                    'avatar': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&q=80',
                }
            )

            SAMPLE_VIDEO_URL = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'

            # =========================================================
            # 2. Course 1: Create & Sell Your First Digital Product With AI
            # =========================================================
            course1, _ = Course.objects.update_or_create(
                slug='create-sell-digital-product-ai',
                defaults={
                    'title': 'Create & Sell Your First Digital Product With AI',
                    'short_description': 'A 3-Hour Practical Session to Take You From Idea to Your First Digital Product.',
                    'description': 'Learn how to find the right niche, identify a real problem, create a digital product with AI, host it online, create promotional content, and launch Meta Ads.',
                    'thumbnail': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&q=80',
                    'instructor': instructor_ai,
                    'category': 'Digital Products & AI',
                    'price': 499.00,
                    'original_price': 2499.00,
                    'duration': '3 Hours',
                    'level': 'Beginner-Friendly',
                    'language': 'English / Hindi Friendly',
                    'is_published': True,
                    'is_bestseller': True,
                    'is_featured': True,
                    'rating': 4.98,
                    'total_ratings': 2840,
                    'total_students': 12500,
                    'learning_outcomes': [
                        'Find your profitable niche that fits your skills, interests, and goals',
                        'Identify a real problem that people actively pay to solve',
                        'Use AI to generate and package high-value digital products in hours',
                        'Host your product online and set up seamless automated delivery',
                        'Create high-converting video and graphic promo content with AI',
                        'Set up and launch high-ROI Meta Ads from scratch',
                        'Scale from an MVP product into recurring digital sales',
                    ],
                    'requirements': [
                        'No technical knowledge or coding needed',
                        'No physical inventory or business setup required',
                        'A computer or smartphone with an internet connection',
                    ],
                }
            )

            c1_modules: List[ModuleData] = [
                {
                    'title': 'Module 1 — Introduction to Digital Products',
                    'order': 1,
                    'lessons': [
                        {
                            'title': 'Lesson 1.1 — The Power of Digital Assets & Zero Inventory Economics',
                            'description': 'This lesson introduces the fundamentals of digital products and explains how they are structured, created, and delivered to customers with zero inventory overhead.\n\nBy the end of this module, you will understand how to calculate break-even economics and structure assets for maximum scale.',
                            'duration': '12:30',
                            'duration_seconds': 750,
                            'is_preview': True,
                            'order': 1,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 1.2 — The 5-Step Formula: Problem → Solution → Package → Promote → Sell',
                            'description': 'Learn the proven 5-step framework to transform your industry knowledge into high-margin digital assets that sell on autopilot.',
                            'duration': '14:20',
                            'duration_seconds': 860,
                            'is_preview': True,
                            'order': 2,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
                {
                    'title': 'Module 2 — Niche Discovery',
                    'order': 2,
                    'lessons': [
                        {
                            'title': 'Lesson 2.1 — Discovering Your Profitable Knowledge Niche',
                            'description': 'Step-by-step breakdown to identify underserved market gaps where customers are actively paying for actionable solutions.',
                            'duration': '15:40',
                            'duration_seconds': 940,
                            'is_preview': False,
                            'order': 3,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 2.2 — AI Prompts for Market & Competitor Analysis',
                            'description': 'Leverage bespoke AI prompts to quickly extract competitor strengths, weaknesses, customer pain points, and pricing strategies.',
                            'duration': '18:15',
                            'duration_seconds': 1095,
                            'is_preview': False,
                            'order': 4,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
                {
                    'title': 'Module 3 — Solve Problems with Digital Products',
                    'order': 3,
                    'lessons': [
                        {
                            'title': 'Lesson 3.1 — Identifying High-Pain Urgent Problems Customers Pay For',
                            'description': 'Discover how to isolate urgent, burning problems that convert casual visitors into immediate buyers.',
                            'duration': '16:10',
                            'duration_seconds': 970,
                            'is_preview': False,
                            'order': 5,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 3.2 — Structuring Your High-Value Solution & Offer',
                            'description': 'Package your knowledge into an irresistible offer structure with clear deliverables and bonuses.',
                            'duration': '14:50',
                            'duration_seconds': 890,
                            'is_preview': False,
                            'order': 6,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
                {
                    'title': 'Module 4 — Create Your Digital Product with AI',
                    'order': 4,
                    'lessons': [
                        {
                            'title': 'Lesson 4.1 — AI-Powered Research, Planning & Outlining SOPs',
                            'description': 'Use structured prompt workflows to plan and outline standard operating procedures, guides, and worksheets in minutes.',
                            'duration': '22:40',
                            'duration_seconds': 1360,
                            'is_preview': False,
                            'order': 7,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 4.2 — Generating Ebooks, Guides, Templates & Toolkits Fast',
                            'description': 'Rapidly format, generate, and polish ready-to-sell toolkits, Notion dashboards, and downloadable templates.',
                            'duration': '25:10',
                            'duration_seconds': 1510,
                            'is_preview': False,
                            'order': 8,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
                {
                    'title': 'Module 5 — Host Your Digital Product',
                    'order': 5,
                    'lessons': [
                        {
                            'title': 'Lesson 5.1 — Instant Hosting & Zero-Code Landing Pages',
                            'description': 'Deploy conversion-optimized product landing pages in under 30 minutes without writing a single line of code.',
                            'duration': '17:30',
                            'duration_seconds': 1050,
                            'is_preview': False,
                            'order': 9,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 5.2 — Automated Checkout, Payments & Digital File Delivery',
                            'description': 'Connect instant payment gateways with automated email receipt dispatch and direct digital asset delivery.',
                            'duration': '19:40',
                            'duration_seconds': 1180,
                            'is_preview': False,
                            'order': 10,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
                {
                    'title': 'Module 6 — Create Content & Sell Your Digital Product',
                    'order': 6,
                    'lessons': [
                        {
                            'title': 'Lesson 6.1 — AI Prompts for Viral Video Scripts, Hooks & Posters',
                            'description': 'Master viral short-form copywriting prompts tailored for Reels, YouTube Shorts, and high-CTR social posters.',
                            'duration': '20:15',
                            'duration_seconds': 1215,
                            'is_preview': False,
                            'order': 11,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 6.2 — Organic Audience Building & Content Distribution',
                            'description': 'A systematic blueprint to build an organic following that reliably feeds targeted traffic into your sales funnel.',
                            'duration': '18:00',
                            'duration_seconds': 1080,
                            'is_preview': False,
                            'order': 12,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
                {
                    'title': 'Module 7 — Set Up & Launch Meta Ads',
                    'order': 7,
                    'lessons': [
                        {
                            'title': 'Lesson 7.1 — Beginner-Friendly Meta Ads Setup & Campaign Architecture',
                            'description': 'Complete walkthrough of Meta Business Manager setup, CAPI configuration, and audience targeting architecture.',
                            'duration': '24:20',
                            'duration_seconds': 1460,
                            'is_preview': False,
                            'order': 13,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 7.2 — Launching, Testing & Scaling Profitable ₹499 Ad Sets',
                            'description': 'Launch and scale profitable ad sets with small daily test budgets while maintaining high ROAS.',
                            'duration': '26:30',
                            'duration_seconds': 1590,
                            'is_preview': False,
                            'order': 14,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
            ]

            self._create_curriculum(course1, c1_modules)

            c1_faqs = [
                {'q': 'Is this suitable for beginners?', 'a': 'Yes. The session starts from the basics and takes you through the complete process step by step.'},
                {'q': 'Do I need technical knowledge?', 'a': 'No. The session is designed to be beginner-friendly.'},
                {'q': 'What type of digital product can I create?', 'a': 'You can create ebooks, guides, templates, checklists, workbooks, toolkits, prompt packs, courses, and other digital resources.'},
                {'q': 'Will I learn how to use AI?', 'a': 'Yes. You\'ll get practical AI prompts and learn how AI can help you with niche discovery, product creation, and marketing.'},
                {'q': 'Will I learn Meta Ads?', 'a': 'Yes. The session covers the basic setup and process for launching Meta Ads to promote your digital product.'},
                {'q': 'How long is the session?', 'a': 'The complete session is approximately 3 hours.'},
                {'q': 'How much does it cost?', 'a': 'The session is available for just ₹499 as a one-time payment.'},
            ]
            self._create_faqs(course1, c1_faqs)

            # =========================================================
            # 3. Course 2: Performance Marketing & Meta Ads Scaling Blueprint
            # =========================================================
            course2, _ = Course.objects.update_or_create(
                slug='performance-marketing-meta-ads-blueprint',
                defaults={
                    'title': 'Performance Marketing & Meta Ads Scaling Blueprint',
                    'short_description': 'Master Modern Meta Ad Buying, Dynamic Creative Testing, and 8-Figure Scaling Strategies.',
                    'description': 'The definitive paid media masterclass covering Advantage+ Shopping Campaigns (ASC), 3:2:2 Dynamic Creative Testing, Server-Side CAPI tracking, post-iOS14 attribution, and vertical/horizontal budget scaling.',
                    'thumbnail': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80',
                    'instructor': instructor_devon,
                    'category': 'Performance Marketing',
                    'price': 1499.00,
                    'original_price': 4999.00,
                    'duration': '6.5 Hours',
                    'level': 'Intermediate to Advanced',
                    'language': 'English',
                    'is_published': True,
                    'is_bestseller': True,
                    'is_featured': True,
                    'rating': 4.96,
                    'total_ratings': 1920,
                    'total_students': 8430,
                    'learning_outcomes': [
                        'Architect modern Advantage+ Shopping and Broad Targeting ad campaigns',
                        'Deploy the 3:2:2 Dynamic Creative Testing (DCT) framework for unbeatable creative velocity',
                        'Calculate exact break-even ROAS, MER (Marketing Efficiency Ratio), and contribution margin',
                        'Implement server-side Meta Conversions API (CAPI) with 8.5+ Event Match Quality',
                        'Scale ad accounts vertically and horizontally with automated safety rules and cost caps',
                        'Brief creators and script UGC videos with >40% 3-second hook retention',
                    ],
                    'requirements': [
                        'Basic familiarity with Meta Ads Manager or eCommerce marketing',
                        'An active ad account or store with intention to run paid traffic',
                        'Commitment to data-driven creative testing and analytics',
                    ],
                }
            )

            c2_modules: List[ModuleData] = [
                {
                    'title': 'Module 1 — Media Buying Foundations & Unit Economics',
                    'order': 1,
                    'lessons': [
                        {
                            'title': 'Lesson 1.1 — Modern Auction Mechanics & Algorithm Signals',
                            'description': 'Understand how Meta evaluates ad rank, estimated action rates, and user value in modern auctions.',
                            'duration': '18:45',
                            'duration_seconds': 1125,
                            'is_preview': True,
                            'order': 1,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 1.2 — The ROAS & MER Calculator (Break-Even Math)',
                            'description': 'Master unit economics: blended MER, Net Contribution Margin, CPA tolerances, and cashflow modeling.',
                            'duration': '21:10',
                            'duration_seconds': 1270,
                            'is_preview': True,
                            'order': 2,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 1.3 — Account Structure & Campaign Architecture',
                            'description': 'Simplify ad account architecture into testing, scaling, and retargeting tiers without audience fragmentation.',
                            'duration': '19:30',
                            'duration_seconds': 1170,
                            'is_preview': False,
                            'order': 3,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
                {
                    'title': 'Module 2 — Dynamic Creative Testing (DCT) Engine',
                    'order': 2,
                    'lessons': [
                        {
                            'title': 'Lesson 2.1 — The 3:2:2 DCT Setup & Iteration Protocol',
                            'description': 'Step-by-step setup of 3 creatives, 2 primary copies, and 2 headlines within sandbox testing ad sets.',
                            'duration': '24:00',
                            'duration_seconds': 1440,
                            'is_preview': False,
                            'order': 4,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 2.2 — Hook Engineering & 3-Second Retention Mastery',
                            'description': 'Battle-tested hook architectures that consistently deliver above 40% thumbstop rates.',
                            'duration': '22:15',
                            'duration_seconds': 1335,
                            'is_preview': False,
                            'order': 5,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 2.3 — UGC Briefing SOPs & Creator Negotiation',
                            'description': 'Systematic workflows to source, brief, and negotiate UGC assets with top creator talent.',
                            'duration': '20:50',
                            'duration_seconds': 1250,
                            'is_preview': False,
                            'order': 6,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
                {
                    'title': 'Module 3 — Advantage+ Campaigns & Broad Scaling',
                    'order': 3,
                    'lessons': [
                        {
                            'title': 'Lesson 3.1 — Advantage+ Shopping Campaigns (ASC) Strategy',
                            'description': 'Configure ASC campaigns with optimal existing-customer caps and machine-learning signals.',
                            'duration': '26:40',
                            'duration_seconds': 1600,
                            'is_preview': False,
                            'order': 7,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 3.2 — Broad Targeting & Audience Expansion',
                            'description': 'How creative serves as your targeting mechanism when running wide-open demographic broad campaigns.',
                            'duration': '17:35',
                            'duration_seconds': 1055,
                            'is_preview': False,
                            'order': 8,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
                {
                    'title': 'Module 4 — Server-Side Tracking & Multi-Touch Attribution',
                    'order': 4,
                    'lessons': [
                        {
                            'title': 'Lesson 4.1 — Meta Conversions API (CAPI) & Server GTM Setup',
                            'description': 'Step-by-step implementation of server-side tracking to bypass ad blockers and browser restrictions.',
                            'duration': '28:10',
                            'duration_seconds': 1690,
                            'is_preview': False,
                            'order': 9,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 4.2 — Post-iOS14 Attribution Modeling & Triple Whale',
                            'description': 'Navigate attribution lag, modeled conversions, and blended dashboards for true revenue visibility.',
                            'duration': '23:45',
                            'duration_seconds': 1425,
                            'is_preview': False,
                            'order': 10,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
                {
                    'title': 'Module 5 — Vertical & Horizontal Scaling Playbook',
                    'order': 5,
                    'lessons': [
                        {
                            'title': 'Lesson 5.1 — Budget Pacing, Automated Rules & Bid Caps',
                            'description': 'Scale aggressively using cost caps, minimum ROAS bidding, and automated stop-loss rules.',
                            'duration': '25:20',
                            'duration_seconds': 1520,
                            'is_preview': False,
                            'order': 11,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 5.2 — Live Media Buyer Checklist & Account Audits',
                            'description': 'Daily and weekly checklist used by senior media buyers to audit performance and cut wasted spend.',
                            'duration': '21:00',
                            'duration_seconds': 1260,
                            'is_preview': False,
                            'order': 12,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
            ]

            self._create_curriculum(course2, c2_modules)

            c2_faqs = [
                {'q': 'Is this program up-to-date with current Meta algorithm changes?', 'a': 'Yes, the entire curriculum is updated for Advantage+ Shopping Campaigns (ASC), CAPI server-side tracking, and latest creative testing methodologies.'},
                {'q': 'What ad spend budget is recommended to apply these strategies?', 'a': 'You can apply these strategies starting with small test budgets (e.g. ₹500 - ₹1,000/day) up to 7-figure monthly ad spend.'},
                {'q': 'Are creative templates and spreadsheets included?', 'a': 'Yes, you receive our plug-and-play Break-Even ROAS Calculator, UGC Briefing SOPs, and 3:2:2 DCT tracking templates.'},
                {'q': 'Do I get access to future updates?', 'a': 'Yes! Enrolled students receive lifetime access to all future modules and framework updates.'},
            ]
            self._create_faqs(course2, c2_faqs)

            # =========================================================
            # 4. Course 3: Full-Stack AI Application Development with Next.js & Python
            # =========================================================
            course3, _ = Course.objects.update_or_create(
                slug='fullstack-ai-nextjs-python',
                defaults={
                    'title': 'Full-Stack AI Application Development with Next.js & Python',
                    'short_description': 'Build & Monetize Production-Ready AI SaaS Apps with LLMs, Vector DBs, and Modern UI.',
                    'description': 'Comprehensive hands-on engineering masterclass. Learn how to architect RAG pipelines, integrate OpenAI/Anthropic models, stream AI responses with Vercel AI SDK, manage vector embeddings with pgvector/Pinecone, and implement recurring Stripe/Razorpay billing.',
                    'thumbnail': 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&q=80',
                    'instructor': instructor_marcus,
                    'category': 'Online Business',
                    'price': 999.00,
                    'original_price': 3499.00,
                    'duration': '8 Hours',
                    'level': 'All Levels',
                    'language': 'English',
                    'is_published': True,
                    'is_bestseller': False,
                    'is_featured': True,
                    'rating': 4.95,
                    'total_ratings': 1140,
                    'total_students': 4200,
                    'learning_outcomes': [
                        'Build full-stack AI applications with Next.js 14 App Router and FastAPI/Django backends',
                        'Implement Production Retrieval-Augmented Generation (RAG) with vector embeddings',
                        'Stream token-by-token AI responses using Vercel AI SDK and Server-Sent Events',
                        'Set up user authentication, session security, and database schemas with PostgreSQL',
                        'Integrate automated subscription billing with Razorpay and Stripe webhooks',
                        'Deploy production AI workloads to Vercel and scalable cloud servers',
                    ],
                    'requirements': [
                        'Basic understanding of JavaScript/TypeScript and Python fundamentals',
                        'A free GitHub and OpenAI/Anthropic API account',
                        'Eagerness to build and ship real-world software products',
                    ],
                }
            )

            c3_modules: List[ModuleData] = [
                {
                    'title': 'Module 1 — AI Architecture & LLM Fundamentals',
                    'order': 1,
                    'lessons': [
                        {
                            'title': 'Lesson 1.1 — High-Performance AI App Architecture',
                            'description': 'System design of modern AI applications: Frontend UI, Gateway APIs, Inference Orchestrators, and Cache layers.',
                            'duration': '20:10',
                            'duration_seconds': 1210,
                            'is_preview': True,
                            'order': 1,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 1.2 — Prompt Engineering, System Prompts & Structured JSON Outputs',
                            'description': 'Mastering function calling, JSON mode, few-shot prompting, and reliable schema guarantees with Pydantic and Zod.',
                            'duration': '24:30',
                            'duration_seconds': 1470,
                            'is_preview': True,
                            'order': 2,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
                {
                    'title': 'Module 2 — Vector Databases & Production RAG Pipelines',
                    'order': 2,
                    'lessons': [
                        {
                            'title': 'Lesson 2.1 — Embeddings, Semantic Search & Chunking Strategies',
                            'description': 'Chunking long documents, generating high-dimension embeddings, and performing cosine similarity searches.',
                            'duration': '28:15',
                            'duration_seconds': 1695,
                            'is_preview': False,
                            'order': 3,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 2.2 — Building Production RAG with pgvector & Hybrid Search',
                            'description': 'Combining dense vector search with sparse keyword search for high-accuracy contextual retrieval.',
                            'duration': '32:00',
                            'duration_seconds': 1920,
                            'is_preview': False,
                            'order': 4,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
                {
                    'title': 'Module 3 — Next.js 14 Streaming UI & Vercel AI SDK',
                    'order': 3,
                    'lessons': [
                        {
                            'title': 'Lesson 3.1 — Next.js App Router & Server Components',
                            'description': 'Optimizing rendering performance with Server Components, Suspense boundaries, and Route Handlers.',
                            'duration': '26:40',
                            'duration_seconds': 1600,
                            'is_preview': False,
                            'order': 5,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 3.2 — Token-by-Token Streaming Chat & Generative UI',
                            'description': 'Creating ChatGPT-style real-time streaming interfaces with markdown rendering and interactive widget generation.',
                            'duration': '30:20',
                            'duration_seconds': 1820,
                            'is_preview': False,
                            'order': 6,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
                {
                    'title': 'Module 4 — Authentication, Billing & Deployment',
                    'order': 4,
                    'lessons': [
                        {
                            'title': 'Lesson 4.1 — User Authentication & Role-Based Access Control',
                            'description': 'Securing your SaaS application with JWT tokens, passwordless magic links, and database access policies.',
                            'duration': '22:50',
                            'duration_seconds': 1370,
                            'is_preview': False,
                            'order': 7,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 4.2 — Subscriptions, Credits & Payment Webhook Handling',
                            'description': 'Implementing token credit metering and recurring subscription payments with idempotency.',
                            'duration': '29:10',
                            'duration_seconds': 1750,
                            'is_preview': False,
                            'order': 8,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 4.3 — Production Deployment & CI/CD Pipelines',
                            'description': 'Deploying to cloud infrastructure with zero downtime and automated continuous integration.',
                            'duration': '19:40',
                            'duration_seconds': 1180,
                            'is_preview': False,
                            'order': 9,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
            ]

            self._create_curriculum(course3, c3_modules)

            c3_faqs = [
                {'q': 'Will I get the complete source code of the project?', 'a': 'Yes! Full GitHub repository access with starter templates, production configs, and boilerplate code is included.'},
                {'q': 'Is this course suitable for beginners in AI?', 'a': 'Yes, we start with the fundamentals of LLM APIs before advancing to complex multi-agent architectures and RAG pipelines.'},
                {'q': 'Can I build my own custom SaaS product using this code?', 'a': 'Absolutely. The architecture is modular and designed to be used as a production foundation for your own commercial products.'},
            ]
            self._create_faqs(course3, c3_faqs)

            # =========================================================
            # 5. Course 4: Mastering High-Ticket Client Acquisition & Agency Scaling
            # =========================================================
            course4, _ = Course.objects.update_or_create(
                slug='high-ticket-client-acquisition-agency',
                defaults={
                    'title': 'Mastering High-Ticket Client Acquisition & Agency Scaling',
                    'short_description': 'Systematic Cold Outreach, Inbound Funnels, and Closing $3,000–$10,000/mo Retainers.',
                    'description': 'A battle-tested agency growth blueprint. Discover how to position your high-ticket offer, build automated cold email infrastructure with AI personalization, run discovery calls that convert, and build automated fulfillment systems.',
                    'thumbnail': 'https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=800&q=80',
                    'instructor': instructor_sarah,
                    'category': 'Online Business',
                    'price': 799.00,
                    'original_price': 2999.00,
                    'duration': '4.5 Hours',
                    'level': 'Beginner to Intermediate',
                    'language': 'English',
                    'is_published': True,
                    'is_bestseller': False,
                    'is_featured': False,
                    'rating': 4.92,
                    'total_ratings': 860,
                    'total_students': 3100,
                    'learning_outcomes': [
                        'Craft an irresistible high-ticket offer that sells for $3,000 - $10,000/month',
                        'Set up automated multi-domain cold email engines sending 1,000+ targeted emails daily',
                        'Conduct friction-free discovery calls and close clients with two-call closing frameworks',
                        'Handle price objections, trust hesitation, and competition with proven scripts',
                        'Build automated client onboarding workflows and standard operating procedures (SOPs)',
                    ],
                    'requirements': [
                        'A marketable skill (marketing, development, design, consulting, video editing, etc.)',
                        'Basic computer and email access',
                        'Commitment to taking daily action on outreach and sales pipeline management',
                    ],
                }
            )

            c4_modules: List[ModuleData] = [
                {
                    'title': 'Module 1 — Offer Positioning & Market Irresistibility',
                    'order': 1,
                    'lessons': [
                        {
                            'title': 'Lesson 1.1 — The Grand Slam B2B Offer Architecture',
                            'description': 'How to package your service so clients perceive 10x ROI and find it irrational to say no.',
                            'duration': '19:15',
                            'duration_seconds': 1155,
                            'is_preview': True,
                            'order': 1,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 1.2 — Pricing Psychology & Retainer Economics',
                            'description': 'Structuring value-based pricing, monthly recurring retainers, and performance bonuses.',
                            'duration': '18:40',
                            'duration_seconds': 1120,
                            'is_preview': True,
                            'order': 2,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
                {
                    'title': 'Module 2 — Automated Outbound & Cold Email Engine',
                    'order': 2,
                    'lessons': [
                        {
                            'title': 'Lesson 2.1 — Domain Setup, SPF/DKIM/DMARC & Warmup Infrastructure',
                            'description': 'Building bulletproof deliverability setups that ensure your emails always land in the primary inbox.',
                            'duration': '22:30',
                            'duration_seconds': 1350,
                            'is_preview': False,
                            'order': 3,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 2.2 — AI Lead Scraping & Personalized Copywriting Formulas',
                            'description': 'Using AI to scrape verified decision-maker emails and craft relevant 3-sentence cold emails.',
                            'duration': '26:00',
                            'duration_seconds': 1560,
                            'is_preview': False,
                            'order': 4,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
                {
                    'title': 'Module 3 — High-Converting Sales Calls & Closing Scripts',
                    'order': 3,
                    'lessons': [
                        {
                            'title': 'Lesson 3.1 — The 45-Minute Discovery & Pitch Framework',
                            'description': 'How to diagnose client bottlenecks, build authority, and pitch your solution naturally.',
                            'duration': '28:45',
                            'duration_seconds': 1725,
                            'is_preview': False,
                            'order': 5,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 3.2 — Overcoming Common Sales Objections in Real Time',
                            'description': 'Word-for-word scripts to handle "It\'s too expensive", "I need to think about it", and "Send me a proposal".',
                            'duration': '24:10',
                            'duration_seconds': 1450,
                            'is_preview': False,
                            'order': 6,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
                {
                    'title': 'Module 4 — Client Onboarding & Automated Fulfillment',
                    'order': 4,
                    'lessons': [
                        {
                            'title': 'Lesson 4.1 — Zero-Friction 24-Hour Client Onboarding Portals',
                            'description': 'Setting up Notion client portals, contracts, and automated invoicing that delight new clients.',
                            'duration': '20:15',
                            'duration_seconds': 1215,
                            'is_preview': False,
                            'order': 7,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                        {
                            'title': 'Lesson 4.2 — Hiring Contractors & Building Delivery SOPs',
                            'description': 'Delegating fulfillment tasks to skilled contractors while preserving high profit margins.',
                            'duration': '21:50',
                            'duration_seconds': 1310,
                            'is_preview': False,
                            'order': 8,
                            'video_url': SAMPLE_VIDEO_URL
                        },
                    ]
                },
            ]

            self._create_curriculum(course4, c4_modules)

            c4_faqs = [
                {'q': 'Is this program only for established agencies?', 'a': 'No, freelancers and solopreneurs looking to transition into high-ticket retainer clients will benefit tremendously.'},
                {'q': 'Are sales scripts and email templates included?', 'a': 'Yes, you receive plug-and-play cold email templates, follow-up sequences, proposal decks, and client contracts.'},
                {'q': 'How quickly can I expect to see results?', 'a': 'Students who implement the outreach infrastructure and follow the sales framework typically book their first qualified discovery calls within 14-21 days.'},
            ]
            self._create_faqs(course4, c4_faqs)

            # =========================================================
            # 6. Create / Update Demo User & Enrolled State
            # =========================================================
            demo_user, u_created = User.objects.get_or_create(
                email='creator@digitalproduct.ai',
                defaults={
                    'name': 'Digital Creator',
                    'avatar': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&q=80',
                    'is_active': True,
                }
            )
            if u_created or not demo_user.check_password('creator123'):
                demo_user.set_password('creator123')
                demo_user.save()

            # Create demo enrollment for Course 1
            first_lesson = Lesson.objects.filter(module__course=course1).first()
            payment, _ = Payment.objects.get_or_create(
                razorpay_order_id='ord_digital_product_demo_01',
                defaults={
                    'user': demo_user,
                    'course': course1,
                    'amount': 49900,
                    'currency': 'INR',
                    'status': 'paid',
                }
            )

            Enrollment.objects.get_or_create(
                user=demo_user,
                course=course1,
                defaults={
                    'payment': payment,
                    'status': 'active',
                    'progress_percentage': 15,
                    'last_watched_lesson': first_lesson,
                    'last_watched_position': 180,
                }
            )

            # =========================================================
            # 7. Create Master Admin
            # =========================================================
            admin_user, _ = User.objects.get_or_create(
                email='admin@learnflow.com',
                defaults={
                    'name': 'Master Admin',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                }
            )
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.is_active = True
            admin_user.set_password('admin123')
            admin_user.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {Course.objects.count()} sample courses, instructors, curriculum, and admin user!'))

    def _create_curriculum(self, course: Course, modules_data: List[ModuleData]):
        for m_info in modules_data:
            module, _ = Module.objects.update_or_create(
                course=course,
                title=m_info['title'],
                defaults={'order': m_info['order']}
            )
            for l_info in m_info['lessons']:
                Lesson.objects.update_or_create(
                    module=module,
                    title=l_info['title'],
                    defaults={
                        'description': l_info['description'],
                        'duration': l_info['duration'],
                        'duration_seconds': l_info['duration_seconds'],
                        'is_preview': l_info['is_preview'],
                        'order': l_info['order'],
                        'video_url': l_info.get('video_url', 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'),
                    }
                )

    def _create_faqs(self, course: Course, faqs_data: list):
        for idx, f in enumerate(faqs_data, start=1):
            FAQ.objects.update_or_create(
                course=course,
                question=f['q'],
                defaults={'answer': f['a'], 'order': idx}
            )
