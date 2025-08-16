# YAML Validator - Docker Setup

A modern, web-based YAML validator with duplicate key detection, built with Django and Bootstrap.

## 🚀 Quick Start with Docker

### Option 1: Using Pre-built Docker Image (Fastest)

1. **Run directly from Docker Hub:**
   ```bash
   docker run -p 8000:8000 duynhvndev/yml-validator:latest
   ```
2. **Access the application:**
   - Open your browser and go to: `http://localhost:8000`

### Option 2: Using Docker Compose (Recommended for Development)

1. **Clone or download this repository**
2. **Run the application:**
   ```bash
   docker-compose up --build
   ```
3. **Access the application:**
   - Open your browser and go to: `http://localhost:8000`

### Option 3: Build from Source

1. **Build the Docker image:**
   ```bash
   docker build -t yml-validator .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 yml-validator
   ```

3. **Access the application:**
   - Open your browser and go to: `http://localhost:8000`

## 🎯 Features

- **YAML Validation**: Comprehensive syntax checking with detailed error reporting
- **Duplicate Key Detection**: Advanced detection of duplicate keys with line numbers
- **YAML Correction**: Automatic formatting and structure correction
- **Modern UI**: Responsive Bootstrap 5 interface with smooth animations
- **Real-time Line Numbers**: Synchronized line numbering with content
- **Copy to Clipboard**: One-click copying of corrected YAML
- **Cross-platform**: Runs anywhere Docker is supported

## 🐳 Docker Configuration

### Environment Variables

- `DJANGO_SETTINGS_MODULE`: Set to `yml_validator.settings` (default)
- `DEBUG`: Set to `True` for development, `False` for production

### Ports

- **8000**: Main application port

### Health Check

The container includes a health check that verifies the application is responding correctly.

## 🔧 Development with Docker

For development with live code reloading:

```bash
docker-compose up
```

The docker-compose.yml mounts the current directory, so changes will be reflected immediately.

## 📦 Production Deployment

For production deployment:

```bash
docker-compose --profile production up -d
```

## 🛠️ Manual Setup (Alternative)

If you prefer to run without Docker:

1. **Install Python 3.8+**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the server:**
   ```bash
   python manage.py runserver
   ```

## 📋 System Requirements

- **Docker**: 20.10+ and Docker Compose 2.0+
- **Memory**: 512MB RAM minimum
- **Storage**: 100MB disk space

## 🎨 Usage

1. **Enter YAML content** in the left panel
2. **Click "Validate"** to check syntax and detect issues
3. **Click "Correct YAML"** to automatically fix formatting
4. **Copy corrected YAML** using the copy button
5. **View detailed error messages** with line numbers for easy debugging

## 🔍 Advanced Features

- **Duplicate Key Detection**: Catches duplicate keys that standard YAML parsers miss
- **Line Number Reporting**: Precise error location identification
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Smooth Animations**: Professional UI with copy notifications and loading states

## 🚨 Troubleshooting

### Container won't start
- Ensure port 8000 is not in use: `lsof -i :8000`
- Check Docker logs: `docker-compose logs`

### Application not accessible
- Verify the container is running: `docker ps`
- Check health status: `docker-compose ps`

### Performance issues
- Increase Docker memory allocation in Docker Desktop settings
- Use production profile for better performance

## 📞 Support

For issues or questions, check the application logs:
```bash
docker-compose logs yml-validator
```

---

**Ready to validate YAML like a pro!** 🎯
