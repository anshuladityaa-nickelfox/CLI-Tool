# Quick Start Guide (5 Minutes)

Get a production-ready Django project running in 5 minutes!

## Step 1: Install Python (If You Don't Have It)

Download Python 3.8+ from [python.org](https://www.python.org/downloads/)

Verify installation:
```bash
python --version
```

## Step 2: Get a Gemini API Key (Free)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key (you'll need it in Step 4)

## Step 3: Setup the Scaffolder

```bash
# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env
```

## Step 4: Add Your API Key

Open `.env` file and replace `your_gemini_api_key_here` with your actual API key:

```
GEMINI_API_KEY=AIzaSyC...your_actual_key_here
```

## Step 5: Generate Your Project

```bash
python main.py create-project
```

Answer the prompts:
- **Project name**: Type any name (e.g., `my_first_project`)
- **Language**: Press `1` and Enter
- **Features**: Type `all` and Enter

Wait 1-2 minutes while AI generates your project...

## Step 6: Run Your Project

### Windows:
```bash
cd my_first_project
quickstart.bat
```

### Linux/Mac:
```bash
cd my_first_project
chmod +x quickstart.sh
./quickstart.sh
```

## Step 7: Open Your Browser

Go to: **http://localhost:8000/**

🎉 **Congratulations!** You now have a running Django project with:
- Admin panel at `/admin/`
- REST API at `/api/`
- Mail services
- Notifications
- File uploads
- Error handling
- Logging system

## What's Next?

1. **Create a superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```

2. **Explore the admin panel**: http://localhost:8000/admin/

3. **Check the API**: http://localhost:8000/api/

4. **Read the docs**: Open `SETUP.md` in your project folder

5. **Start coding**: Modify files in `apps/` directory

## Common Issues

### "GEMINI_API_KEY not found"
- Make sure you created `.env` file
- Make sure you added your API key to `.env`

### "Module not found"
- Run: `pip install -r requirements.txt`

### "Port already in use"
- Close other programs using port 8000
- Or run: `python manage.py runserver 8001`

## Need Help?

- Read `USAGE_GUIDE.md` for detailed instructions
- Check `README.md` for full documentation
- Review `PROJECT_SUMMARY.md` for overview

## Tips

- Use `quickstart` for testing (no superuser needed)
- Use `setup` for full development (creates superuser)
- Keep `.env` file secret (never share your API key)
- Explore the generated code to learn Django best practices

---

**That's it! You're now a Django developer! 🚀**
