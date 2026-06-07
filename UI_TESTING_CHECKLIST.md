# UI Testing Checklist - PuckMind

Comprehensive testing checklist for the PuckMind Streamlit web interface.

---

## 🏠 **Dashboard/Home Tab**

### Quick Action Buttons
- [ ] "➕ Add Game" → navigates to Data Management → Game Wizard section
- [ ] "👥 Update Availability" → navigates to Data Management → Player Availability section
- [ ] "📊 View Stats" → navigates to Chat and triggers "Show me our team statistics"

### Dashboard Widgets
- [ ] Season statistics display correctly (Wins, OT/SO Wins, Losses, OT/SO Losses, Points)
- [ ] European points system: 3pts (W), 2pts (OTW), 1pt (OTL), 0pts (L)
- [ ] Points calculation shown in tooltip (e.g., "5×3 + 2×2 + 3×1 = 22 pts")
- [ ] Recent Results show correct badges: 🟢 Win, 🟢 OT/SO Win, 🟡 OT/SO Loss, 🔴 Loss
- [ ] Top Performers shows top 3 scorers with medals (🥇 🥈 🥉)
- [ ] Next Game widget shows correct upcoming game details
- [ ] Days until calculation is accurate (date-based, not time-based)
- [ ] Team Status shows available/unavailable player counts
- [ ] Unavailable players list displays correctly
- [ ] Goalie Stats show save % and GAA

### Chat Shortcuts
- [ ] All 5 question buttons work and navigate to Chat tab
- [ ] Questions are pre-filled in chat when clicked

---

## 📊 **Data Management Tab**

### Schedule Management
- [ ] **View Mode Toggle:** Can switch between List View and Calendar View
- [ ] **List View:**
  - [ ] Add scheduled game form works (all fields)
  - [ ] Upcoming games display correctly
  - [ ] Home/Away indicator shows properly
  - [ ] Days until calculation is accurate
  - [ ] Game expander shows all details (date, time, location, notes)
  - [ ] **Attendance tracking:**
    - [ ] Confirmed/Declined/Pending counts display
    - [ ] "Coming ✅" marks as confirmed
    - [ ] "Not Coming ❌" marks as declined (not confirmed!)
    - [ ] Warnings show when insufficient players
    - [ ] Quick attendance form works correctly
    - [ ] "View Full Roster" button expands full list
    - [ ] Full roster shows all three categories correctly
  - [ ] **Cancel game button:**
    - [ ] "🗑️ Cancel This Game" button appears
    - [ ] Confirmation dialog appears
    - [ ] "Yes, Cancel Game" removes game from upcoming list
    - [ ] "No, Keep It" cancels the action
  - [ ] Export calendar button downloads .ics file
- [ ] **Calendar View:**
  - [ ] Month/Year selector works
  - [ ] Calendar grid displays correctly
  - [ ] Days with games show 🏒 icon
  - [ ] Game time and opponent show on calendar
  - [ ] Expandable list below calendar shows all games for the month
  - [ ] Only shows scheduled games (excludes cancelled)

### Game Wizard (Add Completed Game)
- [ ] **Step 1: Basic info**
  - [ ] Opponent, date, score entry works
  - [ ] Result type selection (Regular Time vs OT/SO) for wins and losses
  - [ ] European points system properly applied (W=3, OTW=2, OTL=1, L=0)
- [ ] **Step 2: Scorers** - Two modes available
  - [ ] **Goal-by-Goal Mode:**
    - [ ] Enter goals one by one with scorer and assists
    - [ ] Progress bar shows completion
    - [ ] Can edit previous goals
    - [ ] Goalies can be added after goals (optional in Step 3)
  - [ ] **Quick Text Entry Mode:**
    - [ ] Natural language input: "Lukas 2G 1A, Felix 1G, Michael hat trick"
    - [ ] Click "Parse & Match Players" to validate
    - [ ] **Player Matching Step:** Links parsed names to roster
      - [ ] Auto-matches unique names (e.g., "Lukas" → "Lukas Schäfer")
      - [ ] Manual selection for ambiguous names
      - [ ] Shows stats for each parsed player
      - [ ] "Confirm & Continue" disabled until all matched
    - [ ] Validates goals match score
    - [ ] Error message if goals don't add up
- [ ] **Step 3: Player Statistics**
  - [ ] Players from Step 2 appear in "Selected Players"
  - [ ] Can add additional players who played but didn't score
  - [ ] Expandable stat entry for each player (assists, shots, +/-, PIM, hits, blocked shots)
  - [ ] **Goalie Section:**
    - [ ] Select goalie from dropdown
    - [ ] Enter minutes played (1-60)
    - [ ] Can add multiple goalies
    - [ ] Total minutes validation (max 60)
    - [ ] Remove goalie button works
    - [ ] Color warnings if minutes don't add to 60
- [ ] **Step 4: Goalie Stats**
  - [ ] Shows each goalie with minutes played
  - [ ] **Shots Against** input field
  - [ ] **Goals Against** input field (defaults to proportional split)
  - [ ] Save % calculated correctly: (Shots - Goals) / Shots
  - [ ] Preview shows calculated save % with breakdown
- [ ] **Step 5: Review**
  - [ ] All game info displayed correctly
  - [ ] Player stats summary shown
  - [ ] Goalie stats with correct save % calculation
  - [ ] Shows: shots, goals against, saves, save %
  - [ ] Submit button updates all stats in database

### Update Player Availability
- [ ] Current status list shows all players
- [ ] Available/Unavailable status correct for each player
- [ ] Quick Actions form works
- [ ] Status toggle (Available/Unavailable) updates correctly
- [ ] Reason field is optional
- [ ] Update triggers database change and UI refresh

### View Players
- [ ] All players display with correct stats
- [ ] Position-specific stats show correctly:
  - [ ] Goalies: GAA, Save %, Wins, Shutouts
  - [ ] Forwards: Goals, Assists, Shooting %, Faceoff %
  - [ ] Defenders: Plus/Minus, Blocked Shots, Hits

### View Past Games
- [ ] All completed games display
- [ ] Results show correctly (score, opponent, date)
- [ ] Notes display when present

---

## 💬 **Chat Tab**

### Basic Queries
- [ ] "Who is available?" → returns available players
- [ ] "Show top scorers" → returns top scorers
- [ ] "What is our record?" → returns record with European points (W-OTW-L-OTL, total points)
- [ ] "Show recent games" → returns last games
- [ ] "Analyze our recent performance" → returns analysis with correct points (22 pts, not 10 pts)

### Quick Game Entry
- [ ] "Record 4-2 win vs Eagles, Lukas 2G 1A" → agent asks if OT/SO
- [ ] Agent prompts: "Was this decided in regulation or overtime/shootout?"
- [ ] Parser handles different formats correctly
- [ ] Stats update after recording with correct points (3 or 2 for win, 1 or 0 for loss)

### Schedule Commands
- [ ] "Schedule game vs Bears on 2026-06-15" → **agent asks for missing info** (home/away, time, location)
- [ ] Providing all details schedules game successfully
- [ ] "What's our next game?" → returns next scheduled game
- [ ] "Show upcoming games" → returns schedule
- [ ] "Cancel the game against [opponent]" → cancels scheduled game

### Ice Time Analysis (NEW)
- [ ] "Who needs more ice time?" → returns analysis
- [ ] Shows developing players with low ice time
- [ ] Compares current ice time vs team average
- [ ] Considers age, status (veteran/regular/developing)
- [ ] Recommends based on performance metrics (+/-, points)

### Attendance Commands
- [ ] "Mark Lukas as attending for next game" → confirms attendance
- [ ] "Felix can't make the game on June 15" → declines attendance
- [ ] "Show roster for next game" → displays attendance status

### Advanced Queries
- [ ] "Suggest a lineup" → returns visual lineup with rink diagram
- [ ] "Show goalie statistics" → returns goalie stats
- [ ] "Suggest training exercises" → returns training plan
- [ ] "Analyze our performance against Eagles" → returns opponent analysis
- [ ] "Who's on a hot streak?" → returns form tracking

---

## 🔄 **Navigation**

- [ ] Tab buttons at top work (Home, Chat, Data Management)
- [ ] Active tab highlights correctly (primary button)
- [ ] Session state persists during tab switches
- [ ] No duplicate key errors in Streamlit

---

## 📱 **Mobile Responsiveness** (Task #5 - Pending)
- [ ] Dashboard layout adapts to mobile
- [ ] Buttons are tap-friendly
- [ ] Forms work on touch screens
- [ ] Text is readable on small screens

---

## ⚠️ **Error Handling**
- [ ] Empty forms show validation errors
- [ ] Invalid dates rejected
- [ ] Invalid player names show errors
- [ ] Database errors handled gracefully
- [ ] No crashes on edge cases

---

## 📝 **Notes**

**Total Checklist Items: ~70**

**How to Test:**
1. Start the app: `streamlit run app.py`
2. Go through each section systematically
3. Check off items as you verify them
4. Note any bugs or issues found
5. Test on different screen sizes (desktop, tablet, mobile)

**Known Issues:**
- (Add any issues discovered during testing here)

**Test Date:** _____________________  
**Tester:** _____________________  
**Browser/Device:** _____________________  
