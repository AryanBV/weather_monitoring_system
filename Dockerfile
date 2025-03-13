FROM python:3.9-slim

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directories for logs and visualizations
RUN mkdir -p logs visualizations models

# Environment variables (can be overridden at runtime)
ENV OPENWEATHERMAP_API_KEY=""
ENV ENABLE_EMAIL_ALERTS="false"
ENV SMTP_SERVER="smtp.gmail.com"
ENV SMTP_PORT="587"
ENV SMTP_USERNAME=""
ENV SMTP_PASSWORD=""
ENV ALERT_FROM_EMAIL=""
ENV ALERT_TO_EMAILS=""
ENV MONGODB_URI=""

# Run the application
CMD ["python", "main.py"]