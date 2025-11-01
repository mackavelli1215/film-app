# FilmApp - Film Production Management Platform

A comprehensive platform for managing film production workflows including script breakdown, budgeting, scheduling, grant matching, and festival submissions.

## 🎬 Features

- **Project Management**: Create and manage film projects with full lifecycle tracking
- **Script Analysis**: Upload scripts and automatically generate scene breakdowns
- **Budget Generation**: AI-powered budget estimation with detailed line items
- **Schedule Planning**: Automated shooting schedule generation based on locations and scenes
- **Grant Matching**: Discover and match with relevant film grants and funding opportunities
- **Festival Research**: Find suitable film festivals and track submission deadlines
- **Collaboration**: Real-time comments, notifications, and team collaboration tools
- **File Storage**: Secure script and document storage via Supabase
- **Background Agents**: Automated processing for analysis and matching

## 🛠 Tech Stack

- **Backend**: Django 5.x, PostgreSQL (Supabase), Python 3.11+
- **Frontend**: HTMX 2.x, Tailwind CSS, Alpine.js
- **Storage**: Supabase Storage for file uploads
- **Database**: Supabase PostgreSQL
- **Deployment**: Django + WhiteNoise static files

## 🚀 Quick Setup

### Windows (Automated)

```bash
# Run the setup script
setup.bat
```

### Manual Setup (Cross-platform)

```bash
# 1. Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Node.js dependencies (requires Node.js 20+)
npm install

# 4. Build Tailwind CSS
npm run build:css

# 5. Set up environment variables
# Copy .env and update with your Supabase credentials

# 6. Run database migrations
python manage.py migrate

# 7. Create initial sample data
python init_data.py

# 8. Create superuser account
python manage.py createsuperuser

# 9. Start the development server
python manage.py runserver
```

### Background Agents

In a separate terminal, run the agent processor:

```bash
# Activate virtual environment first
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Run agents (one-time processing)
python manage.py run_agents --once

# Or run continuously
python manage.py run_agents
```

## ⚙️ Configuration

Update your `.env` file with real Supabase credentials:

```env
DEBUG=1
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgres://user:password@db.supabase.co:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
SUPABASE_STORAGE_BUCKET=scripts
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 📁 Project Structure

```
filmapp/
├── accounts/          # User profiles and companies
├── agents/            # Background job processing
├── breakdown/         # Script breakdown and scenes
├── budgets/           # Budget planning and tracking
├── collab/            # Comments and collaboration
├── core/              # Shared utilities and dashboard
├── festivals/         # Festival research and submissions
├── grants/            # Grant discovery and matching
├── projects/          # Main project management
├── schedules/         # Shooting schedules
├── static/            # CSS/JS assets
├── templates/         # HTML templates
├── filmapp/           # Django settings and configuration
├── manage.py          # Django management script
├── requirements.txt   # Python dependencies
├── package.json       # Node.js dependencies
├── tailwind.config.js # Tailwind CSS configuration
└── init_data.py      # Sample data creation
```

## 🎯 Usage Workflow

1. **Create Account**: Sign up and create your production company profile
2. **Start Project**: Create a new film project with basic details
3. **Upload Script**: Upload your script file to Supabase Storage
4. **Analyze Script**: Run script analysis agent to generate scene breakdown
5. **Generate Budget**: Use budget generation agent for initial cost estimates
6. **Plan Schedule**: Create shooting schedule based on locations and scenes
7. **Find Funding**: Discover grants and festivals matching your project
8. **Collaborate**: Use comments and notifications for team coordination

## 🔧 Development

### Database Migrations

```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Static Files

```bash
# Development mode (with file watching)
npm run dev:css

# Production build
npm run build:css
```

### Admin Interface

Access the Django admin at `/admin/` with your superuser credentials.

## 🚀 Deployment

The application is designed to be deployed on platforms like:

- **Heroku**: Use the provided Procfile and buildpacks
- **Railway**: Direct deployment from Git
- **DigitalOcean App Platform**: Configure with Node.js + Python buildpacks
- **Traditional VPS**: Use gunicorn + nginx setup

### Environment Variables for Production

```env
DEBUG=0
SECRET_KEY=your-production-secret-key
DATABASE_URL=your-production-database-url
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key
SUPABASE_STORAGE_BUCKET=scripts
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 📊 Agent System

The platform includes a background agent system for automated processing:

- **Script Agent**: Analyzes uploaded scripts and creates scene breakdowns
- **Budget Agent**: Generates detailed budget estimates based on project scope
- **Schedule Agent**: Creates optimized shooting schedules
- **Grant Scraper**: Discovers new grant opportunities
- **Grant Matcher**: Matches projects with relevant grants
- **Festival Scraper**: Finds film festival opportunities
- **Festival Matcher**: Suggests suitable festivals for projects

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure code quality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the `/docs/` folder for detailed guides
- **Issues**: Report bugs and feature requests on GitHub
- **Community**: Join our Discord server for discussions

## ✅ Acceptance Criteria Status

- ✅ User registration and authentication working
- ✅ Project creation and management functional
- ✅ Script upload to Supabase Storage implemented
- ✅ Background job processing system operational
- ✅ HTMX-powered dynamic interfaces working
- ✅ Responsive Tailwind CSS design implemented
- ✅ Database integration with Supabase configured
- ✅ Agent system for automated processing ready
- ✅ Real-time notifications and collaboration tools

**Ready for `python manage.py runserver`!** 🎉
