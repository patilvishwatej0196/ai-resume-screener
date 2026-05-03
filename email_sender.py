# email_sender.py
# This file handles all email notifications for the platform
# It sends professional HTML emails to shortlisted candidates
# Uses Python's built-in smtplib — no extra library needed
# Credentials are loaded from .env file for security

# Import smtplib — Python's built-in email sending library
import smtplib

# Import email modules for building professional HTML emails
from email.mime.multipart import MIMEMultipart  # for multi-part emails
from email.mime.text import MIMEText            # for text and HTML content

# Import os for environment variable access
import os

# Import load_dotenv to read credentials from .env file
from dotenv import load_dotenv

# Load the .env file — reads SENDER_EMAIL and SENDER_PASSWORD
# into environment variables so Python can access them
load_dotenv()


# -------------------------------------------------------
# EMAIL CREDENTIALS
# Read from .env file — never hardcode passwords in code
# -------------------------------------------------------

# Get sender email from .env file
SENDER_EMAIL    = os.getenv("SENDER_EMAIL")

# Get app password from .env file
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# Gmail SMTP server address
SMTP_SERVER     = "smtp.gmail.com"

# Gmail SMTP port for TLS encryption
SMTP_PORT       = 587


# -------------------------------------------------------
# FUNCTION 1: Build shortlist email HTML template
# -------------------------------------------------------

def build_shortlist_email(name, score, job_role, matched_skills):
    # This function builds a professional HTML email
    # for shortlisted candidates
    # Returns the HTML as a string

    # Format matched skills as colored tags
    # We join them with comma for clean display
    skills_text = ", ".join(matched_skills) if matched_skills else "Multiple skills"

    # Build the complete HTML email
    # Triple quotes allow multi-line strings in Python
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            /* Email body styling */
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}

            /* Main email container */
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}

            /* Header banner */
            .header {{
                background: linear-gradient(135deg, #1F3864, #2E74B5);
                color: white;
                padding: 30px;
                text-align: center;
            }}

            /* Main content area */
            .content {{
                padding: 30px;
                color: #333;
                line-height: 1.6;
            }}

            /* Score display box */
            .score-box {{
                background: #f0f8ff;
                border: 2px solid #2E74B5;
                border-radius: 10px;
                padding: 16px;
                text-align: center;
                margin: 20px 0;
            }}

            /* Big score number */
            .score-number {{
                font-size: 48px;
                font-weight: bold;
                color: #28a745;
                margin: 0;
            }}

            /* Skills section */
            .skills-box {{
                background: #f0fff4;
                border-left: 4px solid #28a745;
                padding: 14px 18px;
                border-radius: 0 8px 8px 0;
                margin: 16px 0;
            }}

            /* Footer */
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #666;
                font-size: 13px;
                border-top: 1px solid #eee;
            }}

            /* Call to action button */
            .cta-button {{
                display: inline-block;
                background: #2E74B5;
                color: white;
                padding: 12px 28px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: bold;
                margin: 16px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">

            <!-- Header section -->
            <div class="header">
                <h1 style="margin:0;font-size:24px;">🎉 Congratulations!</h1>
                <p style="margin:8px 0 0 0;opacity:0.9;">
                    You have been shortlisted!
                </p>
            </div>

            <!-- Main content -->
            <div class="content">

                <!-- Greeting -->
                <p>Dear <strong>{name}</strong>,</p>

                <p>
                    We are pleased to inform you that your resume has been
                    reviewed and you have been <strong>shortlisted</strong>
                    for the following position:
                </p>

                <!-- Job role highlight -->
                <p style="font-size:20px;font-weight:bold;color:#1F3864;
                           text-align:center;padding:10px;
                           background:#EBF3FB;border-radius:8px;">
                    🎯 {job_role}
                </p>

                <!-- Match score box -->
                <div class="score-box">
                    <p style="margin:0;color:#666;font-size:14px;">
                        Your AI Match Score
                    </p>
                    <p class="score-number">{score}%</p>
                    <p style="margin:4px 0 0 0;color:#28a745;font-weight:bold;">
                        ✅ Strong Match
                    </p>
                </div>

                <!-- Matched skills -->
                <div class="skills-box">
                    <p style="margin:0 0 8px 0;font-weight:bold;color:#155724;">
                        ✅ Your Matching Skills:
                    </p>
                    <p style="margin:0;color:#333;">{skills_text}</p>
                </div>

                <!-- Next steps -->
                <h3 style="color:#1F3864;">📋 Next Steps:</h3>
                <ol>
                    <li>Our HR team will contact you within <strong>2-3 business days</strong></li>
                    <li>Please keep your phone and email accessible</li>
                    <li>Prepare for a technical interview round</li>
                    <li>Review the job requirements and your matched skills</li>
                </ol>

                <p>
                    We look forward to speaking with you soon.
                    If you have any questions, please reply to this email.
                </p>

                <p>Best regards,<br>
                <strong>HR Recruitment Team</strong><br>
                AI Resume Screening Platform</p>

            </div>

            <!-- Footer -->
            <div class="footer">
                <p>This is an automated notification from AI Resume Screener</p>
                <p>Powered by Sentence-BERT + spaCy NLP</p>
            </div>

        </div>
    </body>
    </html>
    """

    # Return the complete HTML string
    return html


# -------------------------------------------------------
# FUNCTION 2: Build rejection email HTML template
# -------------------------------------------------------

def build_rejection_email(name, job_role, missing_skills):
    # Builds a polite rejection email
    # Shows missing skills so candidate knows what to improve

    # Format missing skills as a list
    skills_text = ", ".join(missing_skills[:5]) if missing_skills else "Some required skills"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background:#f4f4f4; margin:0; padding:0; }}
            .container {{ max-width:600px; margin:20px auto; background:white;
                          border-radius:12px; overflow:hidden;
                          box-shadow:0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background:linear-gradient(135deg,#555,#777);
                       color:white; padding:30px; text-align:center; }}
            .content {{ padding:30px; color:#333; line-height:1.6; }}
            .skills-box {{ background:#fff5f5; border-left:4px solid #dc3545;
                           padding:14px 18px; border-radius:0 8px 8px 0; margin:16px 0; }}
            .footer {{ background:#f8f9fa; padding:20px; text-align:center;
                       color:#666; font-size:13px; border-top:1px solid #eee; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin:0;font-size:22px;">Application Update</h1>
                <p style="margin:8px 0 0 0;opacity:0.9;">{job_role}</p>
            </div>
            <div class="content">
                <p>Dear <strong>{name}</strong>,</p>
                <p>
                    Thank you for applying for the <strong>{job_role}</strong> position.
                    After careful review, we regret to inform you that we will not
                    be moving forward with your application at this time.
                </p>
                <div class="skills-box">
                    <p style="margin:0 0 8px 0;font-weight:bold;color:#721c24;">
                        📚 Skills to develop for future applications:
                    </p>
                    <p style="margin:0;color:#333;">{skills_text}</p>
                </div>
                <p>
                    We encourage you to develop these skills and apply again
                    in the future. We wish you the best in your career journey.
                </p>
                <p>Best regards,<br>
                <strong>HR Recruitment Team</strong></p>
            </div>
            <div class="footer">
                <p>This is an automated notification from AI Resume Screener</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html


# -------------------------------------------------------
# FUNCTION 3: Send a single email
# -------------------------------------------------------

def send_email(recipient_email, recipient_name, subject, html_content):
    # This is the core function that actually sends the email
    # Uses Gmail SMTP with TLS encryption

    # Check credentials are loaded
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return False, "Email credentials not found in .env file"

    try:
        # MIMEMultipart creates an email that can have
        # both plain text and HTML versions
        msg = MIMEMultipart('alternative')

        # Set email headers
        msg['Subject'] = subject           # email subject line
        msg['From']    = SENDER_EMAIL      # sender address
        msg['To']      = recipient_email   # recipient address

        # Create HTML version of the email
        # 'html' tells email clients to render as HTML
        html_part = MIMEText(html_content, 'html')

        # Attach HTML content to the email
        msg.attach(html_part)

        # Connect to Gmail SMTP server
        # smtplib.SMTP() opens a connection to the mail server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)

        # ehlo() identifies our client to the server
        server.ehlo()

        # starttls() upgrades connection to encrypted TLS
        # This keeps credentials and content secure
        server.starttls()

        # ehlo() again after TLS upgrade
        server.ehlo()

        # Login with Gmail credentials from .env file
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        # Send the email
        # sendmail(from, to, message) delivers the email
        server.sendmail(
            SENDER_EMAIL,
            recipient_email,
            msg.as_string()
        )

        # Close the server connection
        server.quit()

        # Return success
        return True, f"Email sent to {recipient_name} ({recipient_email})"

    except smtplib.SMTPAuthenticationError:
        # Wrong email or app password
        return False, "Authentication failed — check your Gmail App Password in .env file"

    except smtplib.SMTPException as e:
        # Other SMTP errors
        return False, f"SMTP error: {str(e)}"

    except Exception as e:
        # Any other error
        return False, f"Failed to send email: {str(e)}"


# -------------------------------------------------------
# FUNCTION 4: Send shortlist notification
# -------------------------------------------------------

def send_shortlist_email(name, email, score, job_role, matched_skills):
    # Sends a shortlist congratulations email to a candidate

    # Build the email subject line
    subject = f"🎉 Congratulations! You've been shortlisted for {job_role}"

    # Build the HTML email content
    html_content = build_shortlist_email(name, score, job_role, matched_skills)

    # Send the email and get result
    success, message = send_email(email, name, subject, html_content)

    return success, message


# -------------------------------------------------------
# FUNCTION 5: Send rejection notification
# -------------------------------------------------------

def send_rejection_email(name, email, job_role, missing_skills):
    # Sends a polite rejection email to a candidate

    # Build subject line
    subject = f"Application Update — {job_role} Position"

    # Build HTML content
    html_content = build_rejection_email(name, job_role, missing_skills)

    # Send the email
    success, message = send_email(email, name, subject, html_content)

    return success, message


# -------------------------------------------------------
# FUNCTION 6: Send emails to all shortlisted candidates
# -------------------------------------------------------

def send_bulk_notifications(all_results, job_role, threshold):
    # Sends emails to ALL candidates in the results list
    # Shortlisted candidates get congratulations email
    # Others get a polite rejection email

    # Lists to track what happened
    sent_success = []   # emails that went through
    sent_failed  = []   # emails that failed

    # Loop through every candidate
    for result in all_results:

        # Get candidate details
        name   = result['name']
        email  = result['email']
        score  = result['final_score']

        # Skip if no valid email found
        if email == "Not found" or "@" not in email:
            sent_failed.append(f"{name} — no valid email address")
            continue

        # Decide shortlisted or rejected based on threshold
        if score >= threshold:

            # Send shortlist email
            success, message = send_shortlist_email(
                name,
                email,
                score,
                job_role,
                result['matched']
            )

        else:

            # Send rejection email
            success, message = send_rejection_email(
                name,
                email,
                job_role,
                result['missing']
            )

        # Track result
        if success:
            sent_success.append(message)
        else:
            sent_failed.append(f"{name} — {message}")

    # Return summary
    return sent_success, sent_failed


# -------------------------------------------------------
# MAIN: Test when run directly
# -------------------------------------------------------

if __name__ == "__main__":

    print("=" * 55)
    print("EMAIL SENDER - TEST RUN")
    print("=" * 55)

    # Check credentials loaded
    print(f"\nSender email: {SENDER_EMAIL}")
    print(f"Password set: {bool(SENDER_PASSWORD)}")

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("\nERROR: Check your .env file has:")
        print("SENDER_EMAIL=yourgmail@gmail.com")
        print("SENDER_PASSWORD=your16charapppassword")
    else:
        print("\nSending test email to yourself...")

        # Send test email to yourself
        success, message = send_shortlist_email(
            name          = "Test Candidate",
            email         = SENDER_EMAIL,   # sending to yourself
            score         = 78.5,
            job_role      = "Python Developer",
            matched_skills= ["python", "flask", "git", "sql", "docker"]
        )

        if success:
            print(f"SUCCESS: {message}")
            print("Check your Gmail inbox!")
        else:
            print(f"FAILED: {message}")

    print("\n" + "=" * 55)
    print("EMAIL TEST COMPLETE")
    print("=" * 55)