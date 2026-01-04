# HTTPS Setup Guide

This guide explains how to enable HTTPS for your YouTube Automation app.

## Option 1: Using Nginx with Let's Encrypt (Recommended for Production)

### Step 1: Install Nginx and Certbot

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx

# macOS (using Homebrew)
brew install nginx certbot
```

### Step 2: Configure Nginx

1. Copy the provided `nginx.conf` to your nginx configuration:
```bash
sudo cp nginx.conf /etc/nginx/sites-available/youtube-automation
sudo ln -s /etc/nginx/sites-available/youtube-automation /etc/nginx/sites-enabled/
```

2. Update the configuration:
   - Replace `your-domain.com` with your actual domain
   - Update paths to match your setup
   - Update Flask app port if different from 5001

3. Test configuration:
```bash
sudo nginx -t
```

4. Start/restart nginx:
```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Step 3: Get SSL Certificate with Let's Encrypt

```bash
# Make sure your domain points to this server
sudo certbot --nginx -d your-domain.com

# Auto-renewal (should be set up automatically)
sudo certbot renew --dry-run
```

### Step 4: Update Flask App

Make sure your Flask app runs on the port specified in nginx.conf (default: 5001).

## Option 2: Using Flask with Self-Signed Certificate (Development Only)

⚠️ **Warning**: Self-signed certificates show security warnings. Use only for development.

### Generate Self-Signed Certificate

```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

### Update run.py

```python
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5001,
        ssl_context=('cert.pem', 'key.pem'),
        debug=False
    )
```

## Option 3: Using Cloudflare (Easiest - Recommended)

1. Sign up for Cloudflare (free plan works)
2. Add your domain to Cloudflare
3. Update DNS nameservers
4. Enable "Always Use HTTPS" in Cloudflare dashboard
5. Cloudflare will handle SSL automatically

Your app can run on HTTP internally, Cloudflare handles HTTPS termination.

## Option 4: Using Caddy (Automatic HTTPS)

Caddy automatically obtains and renews SSL certificates.

1. Install Caddy:
```bash
# macOS
brew install caddy

# Linux
curl https://getcaddy.com | bash
```

2. Create `Caddyfile`:
```
your-domain.com {
    reverse_proxy localhost:5001
}
```

3. Run Caddy:
```bash
caddy run
```

Caddy automatically handles HTTPS!

## Verification

After setup, verify HTTPS is working:
1. Visit `https://your-domain.com`
2. Check browser shows secure lock icon
3. Test redirect from HTTP to HTTPS

## Performance Notes

- All configurations include HTTP/2 support
- Compression is enabled
- Static files are cached
- Security headers are set

