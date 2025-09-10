
# StackHack.live
## 🚀 Features  
- 🔑 **JWT Authentication** (via `djangorestframework-simplejwt`)  
- 🗄 **MySQL Database** integration  
- ☁️ **Cloudinary Storage** for media and static files  
- 🎵 **Audio Analysis & Processing** using `librosa`, `pydub`, and `scikit-learn`  
- 🔗 **RESTful APIs** built with DRF  
- 🌐 **CORS Support** for frontend integration (React/Next.js/Angular etc.)  
- ⚡ **ASGI Support** with `uvicorn` & `gunicorn`  

---

## 🛠 Tech Stack  
- **Backend Framework:** Django 5.2.4  
- **API Framework:** Django REST Framework 3.16.0  
- **Authentication:** JWT (SimpleJWT)  
- **Database:** MySQL  
- **Media Storage:** Cloudinary  
- **Audio/ML:** librosa, scikit-learn, scipy, numpy  
- **Deployment:** Gunicorn, Uvicorn  

---

## 📦 Installation & Setup  

### 1️⃣ Clone the repository  
```bash
git clone https://github.com/gwc-sys/StackHack.live-Backend.git
cd StackHack.live-Backend

2️⃣ Create a virtual environment

python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows

3️⃣ Install dependencies

pip install -r requirements.txt

4️⃣ Setup environment variables

Create a .env file in the root directory:

DEBUG=True
SECRET_KEY=your_django_secret_key
DATABASE_NAME=your_db_name
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
DATABASE_PORT=3306

# Cloudinary config
CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@<cloud_name>

5️⃣ Apply migrations

python manage.py migrate

6️⃣ Run the development server

python manage.py runserver

or with Uvicorn:

uvicorn backend.asgi:application --reload


⸻

📂 Project Structure

StackHack.live-Backend/
│── backend/              # Django project core
│── api/                  # REST API apps
│── manage.py             # Django management script
│── requirements.txt      # Dependencies
│── .env.example          # Example environment variables


⸻

🔐 Authentication

This project uses JWT authentication.
	•	Obtain a token: POST /api/token/
	•	Refresh a token: POST /api/token/refresh/
	•	Use in headers:

Authorization: Bearer <your_token>



⸻

📡 Example API Endpoints

Auth

POST /api/token/            # Login and get JWT token
POST /api/token/refresh/    # Refresh JWT token

Users

POST /api/users/register/   # Register a new user
GET  /api/users/me/         # Get current user profile

Audio

POST /api/audio/upload/     # Upload an audio file
GET  /api/audio/analyze/    # Run audio analysis


⸻

🌍 Deployment

For production, use Gunicorn with Uvicorn workers:

gunicorn backend.asgi:application -k uvicorn.workers.UvicornWorker


⸻

🤝 Contributing

Contributions are welcome! Please fork this repo and submit a pull request.

⸻

📜 License

This project is licensed under the MIT License.

---

👉 Do you want me to also **generate a `.env.example` file** so contributors know exactly which environment variables to set up?
