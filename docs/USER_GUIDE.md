# User Guide - Smart Voice Interviewer

Welcome to the Smart Voice Interviewer! This guide will help you get started and make the most of the platform.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Registration & Login](#registration--login)
3. [Dashboard Overview](#dashboard-overview)
4. [Starting an Interview](#starting-an-interview)
5. [During the Interview](#during-the-interview)
6. [After the Interview](#after-the-interview)
7. [Tracking Your Progress](#tracking-your-progress)
8. [Achievements System](#achievements-system)
9. [Profile Management](#profile-management)
10. [Tips for Success](#tips-for-success)
11. [FAQ](#faq)
12. [Troubleshooting](#troubleshooting)

---

## Getting Started

### What is Smart Voice Interviewer?

Smart Voice Interviewer is an AI-powered platform that helps you prepare for technical interviews through realistic practice sessions. The platform:

- **Asks real interview questions** from various technical domains
- **Uses voice recognition** so you can practice speaking your answers
- **Evaluates your responses** using advanced AI (Sentence-BERT)
- **Provides instant feedback** with scores and explanations
- **Tracks your progress** with detailed analytics and achievements

### System Requirements

**Browser:**
- Google Chrome (recommended)
- Microsoft Edge
- Firefox (limited voice support)

**Hardware:**
- Microphone (for voice input)
- Speakers or headphones
- Stable internet connection

**Permissions:**
- Microphone access (for voice answers)

---

## Registration & Login

### Creating an Account

1. **Navigate to the home page**
   - Visit `http://localhost:5173` (or your production URL)

2. **Click "Get Started Free"**
   - You'll see a modal with Login/Register tabs

3. **Switch to Register tab**

4. **Fill in your information:**
   - **Username** (required): Your unique identifier
   - **Email** (required): For account recovery
   - **Password** (required): At least 6 characters
   - **Full Name** (required): Your display name
   - **Bio** (optional): Tell us about yourself
   - **Experience Level** (required): 
     - Beginner: Just starting out
     - Intermediate: 1-3 years experience
     - Advanced: 3-5 years experience
     - Expert: 5+ years experience

5. **Click "Register"**
   - Your account will be created instantly
   - You'll be automatically logged in
   - Redirected to your dashboard

### Logging In

1. **Click "Login" button** in the header or home page

2. **Enter credentials:**
   - Username or email
   - Password

3. **Click "Login"**
   - You'll be redirected to your dashboard

### Forgot Password?

Currently, password reset is not available through the UI. Contact support or:
1. Access the backend database
2. Generate a new password hash
3. Update the user record manually

---

## Dashboard Overview

Your dashboard is your command center. Here's what you'll see:

### Top Section - Welcome Banner
```
Welcome back, [Your Name]! 👋
Ready to sharpen your skills today?
[Start New Interview Button]
```

### Stats Grid (4 Cards)

#### 1. Total Interviews
- Shows number of completed interview sessions
- Updates after each completed interview

#### 2. Pass Rate
- Average score across all interviews
- Calculated as: (Total Score / Total Interviews)
- Green when above 60%, yellow 40-60%, red below 40%

#### 3. Day Streak
- Number of consecutive days you've practiced
- Resets if you miss a day
- Flame icon lights up when active

#### 4. Achievements
- Number of unlocked achievements
- Click to view all achievements

### Recent Activity
- Shows your last 3 interview sessions
- Each entry displays:
  - Topic/Category
  - Number of questions
  - Score percentage
  - Pass/Fail status
  - Date completed
- **View All** button shows complete history

### Quick Actions
Three cards for quick access:

1. **Start Interview** - Begin a new practice session
2. **View Achievements** - See all unlocked badges
3. **View History** - See all past interviews

---

## Starting an Interview

### Step 1: Choose Your Settings

1. **Click "Start Interview"** from:
   - Dashboard
   - Home page (when authenticated)
   - Header button

2. **Select Category:**
   ```
   Available categories:
   - Python
   - JavaScript
   - Java
   - Data Structures
   - Algorithms
   - System Design
   - Databases
   - React
   - Node.js
   - And more...
   ```

3. **Choose Number of Questions:**
   - Slider from 1 to 20 questions
   - Recommended:
     - Quick practice: 3-5 questions
     - Regular session: 5-10 questions
     - Full interview: 15-20 questions

4. **Enable/Disable Voice Input:**
   - Toggle switch for microphone
   - If disabled, you'll type your answers
   - If enabled, you can speak (and still type as backup)

### Step 2: Start the Session

1. **Click "Start Interview"**
   - Questions are randomly selected
   - Session ID is generated
   - Timer starts

2. **Allow Microphone Access** (if using voice)
   - Browser will ask for permission
   - Click "Allow"
   - You only need to do this once

---

## During the Interview

### Question Screen Layout

```
┌─────────────────────────────────────────┐
│  Question 3 of 10 - Python    [Timer]  │
├─────────────────────────────────────────┤
│                                         │
│  What is a list comprehension in        │
│  Python? Explain with an example.       │
│                                         │
│  [🔊 Speak Question]                    │
├─────────────────────────────────────────┤
│  Your Answer:                           │
│  ┌─────────────────────────────────┐   │
│  │                                 │   │
│  │  [Microphone icon] Recording... │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [🎤 Start Recording] [⏹ Stop]         │
│  [✅ Submit Answer]                     │
└─────────────────────────────────────────┘
```

### Using Voice Input

1. **Click the microphone icon** 🎤
   - Red dot appears (recording)
   - Speak clearly and naturally
   - You can pause while recording

2. **Tips for best results:**
   - Speak at normal conversational pace
   - Use proper technical terms
   - Give complete explanations
   - Avoid long pauses (may stop recording)

3. **Review your transcript:**
   - Your spoken words appear as text
   - Edit if needed before submitting
   - You can type additional content

4. **Click "Stop" when done**
   - Recording ends
   - Text is finalized

### Using Text Input

1. **Simply type your answer** in the text area
2. **Format your response** (plain text only)
3. **No time limit** - take your time

### Submitting Your Answer

1. **Review your response**
2. **Click "Submit Answer"**
3. **Instant feedback appears:**
   ```
   ┌─────────────────────────────────────┐
   │  Score: 85.5 / 100  ✅             │
   │  Correct!                           │
   ├─────────────────────────────────────┤
   │  Feedback:                          │
   │  Excellent explanation! You         │
   │  covered the key concepts of list   │
   │  comprehensions including syntax    │
   │  and practical examples.            │
   ├─────────────────────────────────────┤
   │  Expected Answer:                   │
   │  A list comprehension is a concise  │
   │  way to create lists in Python...   │
   └─────────────────────────────────────┘
   ```

4. **Click "Next Question"** to continue

### Score Breakdown

- **90-100**: Excellent! Complete and accurate
- **75-89**: Very Good! Minor details missing
- **60-74**: Good! Core concepts covered
- **40-59**: Fair - Missing key points
- **Below 40**: Needs improvement

---

## After the Interview

### Results Screen

After completing all questions, you'll see:

```
┌─────────────────────────────────────────────┐
│        🎉 Interview Complete! 🎉           │
├─────────────────────────────────────────────┤
│  Final Score: 82.3 / 100                   │
│  Status: PASSED ✅                         │
│  Questions: 5                               │
│  Time: 7 minutes 30 seconds                │
├─────────────────────────────────────────────┤
│  Performance Breakdown:                     │
│  Question 1: 90.0 ✅                       │
│  Question 2: 75.0 ✅                       │
│  Question 3: 85.5 ✅                       │
│  Question 4: 80.0 ✅                       │
│  Question 5: 81.0 ✅                       │
├─────────────────────────────────────────────┤
│  🏆 New Achievement Unlocked!              │
│  "First Interview"                         │
│  Completed your first interview            │
└─────────────────────────────────────────────┘

[Back to Dashboard]  [Start Another Interview]
```

### Celebration Effects

- **Confetti animation** for passing (≥60%)
- **Fireworks** for excellent performance (≥90%)
- **Achievement popup** for new unlocks

### What Happens Next

1. **Stats are updated:**
   - Interview count increases
   - Average score recalculated
   - Streak updated (if daily)

2. **History is saved:**
   - Full session details stored
   - Questions and answers recorded
   - Scores archived

3. **Achievements checked:**
   - System evaluates if you earned any badges
   - Notifications appear for new achievements

---

## Tracking Your Progress

### Interview History

**Access:** Click "History" icon in header or dashboard

#### History View Features:

```
┌───────────────────────────────────────────────┐
│  Interview History                            │
│  [Filter by Category ▼] [Show: All ▼]       │
├───────────────────────────────────────────────┤
│  📅 Jan 20, 2026                             │
│  ✅ Python Interview                          │
│  Score: 85.5% (5 questions)                  │
│  Time: 7 min 30 sec                          │
│  [View Details]                              │
├───────────────────────────────────────────────┤
│  📅 Jan 19, 2026                             │
│  ✅ JavaScript Interview                      │
│  Score: 78.0% (3 questions)                  │
│  Time: 5 min 15 sec                          │
│  [View Details]                              │
└───────────────────────────────────────────────┘
```

#### Viewing Details

Click "View Details" to see:
- Each question asked
- Your answer
- Expected answer
- Individual scores
- Feedback for each

### Analytics Dashboard

#### Performance Trends (Coming Soon)
- Line chart of scores over time
- Category-wise performance
- Improvement rate
- Weak areas identification

#### Time Analysis
- Average time per question
- Fastest/slowest sessions
- Time of day performance

---

## Achievements System

### How Achievements Work

- Unlocked automatically when criteria met
- Can be earned retroactively
- Permanent once unlocked
- Display in profile and dashboard

### Available Achievements

#### 🏆 First Interview
- **Requirement:** Complete your first interview
- **When:** After first session

#### ⭐ Perfect Score
- **Requirement:** Score 100% on any interview
- **When:** After perfect session

#### 🔥 Practice Marathon
- **Requirement:** Complete 10 interviews
- **When:** After 10th session

#### 📅 Week Warrior
- **Requirement:** Practice 7 days in a row
- **When:** After 7-day streak

#### 💎 Perfect Streak
- **Requirement:** Score 90%+ five times in a row
- **When:** After 5th consecutive high score

#### 👑 Interview Master
- **Requirement:** Complete 50 interviews
- **When:** After 50th session

#### ⚡ Speed Demon
- **Requirement:** Complete interview in under 5 minutes
- **When:** After fast session (5+ questions)

#### 📚 Knowledge Seeker
- **Requirement:** Practice in 5 different categories
- **When:** After 5th unique category

### Viewing Achievements

**Access:** Click "Achievements" icon (trophy) in header

```
┌────────────────────────────────────────┐
│  Your Achievements (3/8)               │
│  Progress: 37.5%                       │
├────────────────────────────────────────┤
│  🏆 First Interview         ✅         │
│  Completed your first interview        │
│  Unlocked: Jan 15, 2026               │
├────────────────────────────────────────┤
│  ⭐ Perfect Score           🔒         │
│  Score 100% on any interview           │
│  Not unlocked yet                      │
└────────────────────────────────────────┘
```

---

## Profile Management

### Viewing Your Profile

**Access:** Click profile avatar in header

### Profile Information

- **Username**: Cannot be changed
- **Email**: Cannot be changed currently
- **Name**: Can update
- **Bio**: Can update
- **Experience Level**: Can update
- **Interests**: Can update (coming soon)

### Updating Profile

1. Click **"Edit Profile"**
2. Modify fields
3. Click **"Save Changes"**
4. Confirmation appears

### Profile Stats

Your profile shows:
- Total interviews
- Average score
- Current streak
- Longest streak
- Join date
- Last interview date

---

## Tips for Success

### 1. Preparation Tips

- **Choose appropriate difficulty:**
  - Beginner: Start with fundamentals
  - Advanced: Challenge yourself

- **Start small:**
  - Do 3-5 questions first
  - Build up to longer sessions

- **Practice regularly:**
  - Daily practice builds streak
  - Consistency improves retention

### 2. During Interview Tips

- **Speak clearly:**
  - Use proper pronunciation
  - Avoid background noise

- **Be comprehensive:**
  - Explain concepts fully
  - Give examples when relevant
  - Mention edge cases

- **Structure your answers:**
  - Introduction
  - Main explanation
  - Example
  - Conclusion

### 3. Learning Tips

- **Review wrong answers:**
  - Read expected answers carefully
  - Understand why you missed points

- **Take notes:**
  - Keep a journal of weak areas
  - Review regularly

- **Practice diverse topics:**
  - Don't stick to one category
  - Build broad knowledge

### 4. Voice Input Tips

- **Find quiet environment**
- **Speak at normal pace**
- **Pause briefly between concepts**
- **Enunciate technical terms**
- **Review transcript before submitting**

---

## FAQ

### General Questions

**Q: Is this platform free?**
A: Currently yes! Full access to all features.

**Q: Do I need to create an account?**
A: Yes, to save your progress and track achievements.

**Q: Can I practice without voice input?**
A: Yes! Toggle off voice and type your answers.

**Q: How are answers evaluated?**
A: Using Sentence-BERT AI model for semantic similarity.

### Technical Questions

**Q: Why isn't the microphone working?**
A: Check browser permissions and use Chrome/Edge.

**Q: Can I pause an interview?**
A: Not currently - complete once started.

**Q: Are questions random?**
A: Yes, randomly selected from the category.

**Q: Can I retake the same interview?**
A: Yes, but questions will be different.

### Scoring Questions

**Q: What's a passing score?**
A: 60% or higher is considered passing.

**Q: Why did I get a low score?**
A: Check expected answer - you may have missed key concepts.

**Q: Can I dispute a score?**
A: Currently no - AI scoring is automated.

**Q: Does voice affect my score?**
A: No, only the content is evaluated, not how it's input.

### Progress Questions

**Q: How do streaks work?**
A: Complete at least one interview per day to maintain.

**Q: When do achievements unlock?**
A: Immediately after meeting criteria.

**Q: Can I lose achievements?**
A: No, achievements are permanent.

**Q: Where is my data stored?**
A: Securely in our database, encrypted and private.

---

## Troubleshooting

### Login Issues

**Problem:** Can't log in
- Check username/password spelling
- Ensure account was created successfully
- Try clearing browser cache
- Contact support if persistent

**Problem:** Forgot password
- Currently no self-service reset
- Contact admin for manual reset

### Interview Issues

**Problem:** Questions not loading
- Check internet connection
- Refresh the page
- Check if backend is running
- Try different category

**Problem:** Can't submit answer
- Ensure answer is not empty
- Check internet connection
- Try typing instead of voice

**Problem:** Low scores on correct answers
- AI may interpret differently
- Check expected answer format
- Try being more specific
- Include examples

### Voice Issues

**Problem:** Microphone not detected
- Grant browser permissions
- Check system microphone settings
- Try different browser (Chrome recommended)
- Check if microphone works in other apps

**Problem:** Voice not transcribing
- Speak louder
- Reduce background noise
- Speak more slowly
- Check microphone distance

**Problem:** Wrong words transcribed
- Speak more clearly
- Use proper pronunciation
- Manually edit transcript
- Switch to typing if persistent

### Performance Issues

**Problem:** Slow loading
- Check internet speed
- Close other browser tabs
- Clear browser cache
- Check if backend is overloaded

**Problem:** Page freezing
- Refresh the page
- Check browser console for errors
- Try incognito mode
- Update browser

---

## Support

### Getting Help

**Documentation:**
- [Main README](../README.md)
- [API Documentation](API.md)
- [Developer Guide](DEVELOPER.md)

**Contact:**
- Email: support@smartvoiceinterviewer.com
- Issues: GitHub Issues page
- Community: GitHub Discussions

### Reporting Bugs

When reporting issues, include:
1. Steps to reproduce
2. Expected vs actual behavior
3. Browser and OS
4. Screenshots if relevant
5. Console errors if any

---

## What's Next?

### Upcoming Features

- Mobile app
- Video recording
- Custom question sets
- Team competitions
- Progress charts
- Export reports to PDF

### Stay Updated

- Check our GitHub for updates
- Join our community
- Follow us on social media

---

**Happy Practicing! 🚀**

Remember: Practice makes perfect. The more you use the platform, the better you'll become at interviews. Good luck! 🎯
