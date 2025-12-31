# AI Detection Test Cases

## Test Case 1: AI-Generated Resume (Should be REJECTED)

```
Results-driven professional with extensive experience in data science and machine learning. 
Proven track record of leveraging advanced analytics to drive business outcomes and deliver 
value-added solutions. Detail-oriented individual with strong analytical skills and excellent 
communication abilities. Demonstrated ability to spearhead complex projects and orchestrate 
cross-functional teams. Proficient in Python, R, and SQL with a strong foundation in 
statistical modeling. Highly motivated team player with a passion for continuous learning 
and professional development. Seeking to leverage my expertise in a challenging role where 
I can contribute to organizational success.

Core Competencies:
- Data Science and Machine Learning
- Advanced Analytics
- Statistical Modeling
- Python, R, SQL
- Team Leadership
- Project Management
- Strategic Planning

Professional Experience:
Utilized cutting-edge technologies to implement scalable solutions. Spearheaded multiple 
initiatives resulting in significant improvements. Collaborated with stakeholders to deliver 
best-in-class outcomes. Orchestrated data-driven strategies to optimize business processes.
```

## Test Case 2: Human-Written Resume (Should be ACCEPTED)

```
I'm a data scientist who's been coding since high school - started with Python building 
a Reddit bot that still runs today (12k users!). Spent the last 3 years at TechCorp where 
I built a customer churn prediction model that saved the company about $2M annually. 
That was pretty cool.

My day-to-day involves Python, pandas, scikit-learn, and lots of SQL queries. Recently 
got into deep learning - built a sentiment analyzer for our support tickets using BERT. 
It wasn't perfect, but it helped our team prioritize urgent issues 40% faster.

I actually enjoy the messy parts of data work - cleaning datasets, debugging pipeline 
failures at 2am, explaining technical stuff to non-technical folks. Also run a small 
blog where I write about ML experiments that failed (there are many).

Skills I use regularly:
- Python (pandas, numpy, scikit-learn, TensorFlow)
- SQL and database stuff
- Git (mostly fixing my own merge conflicts)
- Tableau for quick dashboards
- A/B testing and stats

Looking for a place where I can keep learning and work on products that actually matter 
to people. Bonus points if there's a good coffee machine.
```

## Test Case 3: Borderline Case (Warning but proceeds)

```
Experienced software engineer with 5 years in full-stack development. I've worked on 
various projects ranging from e-commerce platforms to mobile applications. Strong skills 
in JavaScript, React, Node.js, and MongoDB.

At my current company, I developed a real-time chat application that handles 10,000+ 
concurrent users. Also improved our API response time by 60% through database optimization. 
I enjoy problem-solving and learning new technologies.

Technical Skills:
- Frontend: React, Vue.js, HTML/CSS, TypeScript
- Backend: Node.js, Express, Python, Django
- Database: MongoDB, PostgreSQL, Redis
- Tools: Git, Docker, AWS, CI/CD

I'm a team player who values clean code and good documentation. Looking forward to 
contributing to challenging projects and growing with a dynamic team.
```

---

## How to Test:

1. **Copy** one of the test cases above
2. **Paste** into the Resume text area in the app
3. **Add any job description** in the JD field
4. **Click "Analyze Resume"**
5. **Observe** the AI detection results:
   - Test Case 1: Should show **❌ REJECTED** (AI-generated)
   - Test Case 2: Should show **✅ ACCEPTED** (Human-written)
   - Test Case 3: Should show **⚠️ WARNING** (Borderline)

---

## Detection Features:

✅ **Perplexity Analysis** - Measures text predictability
✅ **Burstiness Check** - Analyzes sentence variation
✅ **AI Phrase Detection** - Identifies common AI clichés
✅ **Repetition Score** - Finds repetitive patterns
✅ **Formality Analysis** - Checks for overly formal language

The system uses multiple signals to determine if content is AI-generated with 60%+ confidence threshold for rejection.
