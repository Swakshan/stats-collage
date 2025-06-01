from pprint import pp
from datetime import datetime, timedelta
from pytz import timezone
from PIL import Image, ImageFont, ImageDraw
from modal import (
    IMG_TRACK,
    IMG_ARTIST,
    IMG_ALBUM,
    LASTM_IMG_DAILY_CHART,
    LASTM_IMG_HOURLY_CHART,
    IMG_TEMP,
    IMG_CALENDAR_TEMP,
    IMG_CALENDAR,
    IMG_FINAL,
    LASTM_IMG_DAY_CHART,
    LASTM_IMG_WEEKLY_CHART,
    FONT_ROBOTO_SEMI_BOLD,
    OUT_IMG_W,
    OUT_IMG_H,
)
from modal import MusicData
from providers.lastfm import (
    getRecentTracksTimestamp,
    getTopAlbums,
    getTopArtists,
    getTopTracks,
    findTopRatings,
    getDurationSpent,
)
from common import (
    buildChart,
    getMonthlyTimestamps,
    getWeeklyTimestamps,
    weekLabel,
    monthLabel,
    timeSpentLabel,
)


# LASTFM
def combineImages(items):
    lenItems = len(items)
    h, w = 720, lenItems * 720
    combineImage = Image.new("RGB", (w, h))

    for i in range(lenItems):
        item: MusicData = items[i]
        img: Image = item.generateImage()
        combineImage.paste(img, (i * h, 0))

    combineImage = combineImage.resize(
        [1440, 288]
    )  # [int(combineImage.width*0.4),int(combineImage.height*0.4)]
    return combineImage


def saveTopItems(start, end):
    tops, counts = findTopRatings(start, end)

    topArtists, topAlbums, topTracks = tops[0], tops[1], tops[2]

    combineImages(getTopArtists(topArtists)).save(IMG_ARTIST)
    print("IMG: Artists saved")

    combineImages(getTopAlbums(topAlbums)).save(IMG_ALBUM)
    print("IMG: Albums saved")

    combineImages(getTopTracks(topTracks)).save(IMG_TRACK)
    print("IMG: Tracks saved")

    return counts


def saveWeeklyCharts(start, end):
    tracks = getRecentTracksTimestamp(start, end)
    hrly = {}
    freq = {}
    startFreqDate = datetime.fromtimestamp(start)

    for i in range(7):
        date = (startFreqDate + timedelta(days=i)).strftime("%d-%m")
        freq[date] = 0

    for ts in tracks:
        hr = ts.strftime("%I%p")
        hrly[hr] = hrly.get(hr, 0) + 1

        date = ts.strftime("%d-%m")
        freq[date] = freq.get(date, 0) + 1

    buildChart(
        "Daily listen pattern",
        freq.keys(),
        freq.values(),
        "Date",
        "Count",
        "#005582",
        LASTM_IMG_DAILY_CHART,
    )
    buildChart(
        "Hourly listen pattern",
        hrly.keys(),
        hrly.values(),
        "Hour",
        "Count",
        "#00c2c7",
        LASTM_IMG_HOURLY_CHART,
    )


def saveMothlyCharts(start, end):
    tracks = getRecentTracksTimestamp(start, end)
    weekly = {}
    days = {"Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0, "Sun": 0}

    for ts in tracks:
        day = ts.strftime("%a")
        days[day] = days.get(day, 0) + 1

        week = int(ts.strftime("%W")) + 1
        weekly[week] = weekly.get(week, 0) + 1

    buildChart(
        "Weekly listen pattern",
        weekly.keys(),
        weekly.values(),
        "Week",
        "Count",
        "#EEDE54",
        LASTM_IMG_WEEKLY_CHART,
    )
    buildChart(
        "Days pattern",
        days.keys(),
        days.values(),
        "Day",
        "Count",
        "#48A54C",
        LASTM_IMG_DAY_CHART,
    )


def saveCollage(lHeader, rHeader, chart1, chart2, counts):
    BG = Image.open(IMG_TEMP)
    x = 25

    draw = ImageDraw.Draw(BG)
    if len(lHeader):
        font = ImageFont.truetype(FONT_ROBOTO_SEMI_BOLD, 80)
        draw.text((x, 15), lHeader, font=font, stroke_width=18, stroke_fill="#000")
    if len(rHeader):
        font = ImageFont.truetype(FONT_ROBOTO_SEMI_BOLD, 60)
        draw.text(
            (x + 1000, 30), rHeader, font=font, stroke_width=18, stroke_fill="#000"
        )

    ALBUM = Image.open(
        IMG_ALBUM
    )  # .resize([1440, 288]) #[int(ALBUM.width*0.4),int(ALBUM.height*0.4)]
    ARTIST = Image.open(IMG_ARTIST)  # .resize([1440, 288])
    TRACK = Image.open(IMG_TRACK)  # .resize([1440, 288])

    y = 215
    offset = 385
    font = ImageFont.truetype(FONT_ROBOTO_SEMI_BOLD, 50)
    BG.paste(ARTIST, (x, y))
    BG.paste(ALBUM, (x, y + offset))
    BG.paste(TRACK, (x, y + (offset * 2)))
    fontX = x + 360
    fontY = y - 76
    draw.text((fontX, fontY), counts[0], font=font, stroke_width=18, stroke_fill="#000")
    draw.text(
        (fontX, fontY + offset),
        counts[1],
        font=font,
        stroke_width=18,
        stroke_fill="#000",
    )
    draw.text(
        (fontX, fontY + (offset * 2)),
        counts[2],
        font=font,
        stroke_width=18,
        stroke_fill="#000",
    )

    CHART1 = Image.open(chart1).resize([1465, 550])
    CHART2 = Image.open(chart2).resize([1465, 550])

    y = 1300
    offset = 540
    BG.paste(CHART1, (x - 30, y))
    BG.paste(CHART2, (x - 30, y + offset))

    BG = BG.resize((OUT_IMG_W, OUT_IMG_H))
    # # Displaying the image
    BG.save(IMG_FINAL, optimize=True)
    print("IMG: Collage saved")
    # BG.show()


def buildWeekly():
    start, end = getWeeklyTimestamps()
    dayCounter, weekCounter = weekLabel(start)
    print("LOG: Building for " + dayCounter)

    counts = saveTopItems(start, end)
    saveWeeklyCharts(start, end)

    saveCollage(
        weekCounter, dayCounter, LASTM_IMG_DAILY_CHART, LASTM_IMG_HOURLY_CHART, counts
    )

    msg = f"#Music {weekCounter}\n{dayCounter}"
    return msg, IMG_FINAL


def buildMonthly():
    start, end = getMonthlyTimestamps()
    mName, mDays = monthLabel(start, end)

    print("LOG: Building for " + mName)

    counts = saveTopItems(start, end)
    saveMothlyCharts(start, end)

    saveCollage(mName, mDays, LASTM_IMG_DAY_CHART, LASTM_IMG_WEEKLY_CHART, counts)

    msg = f"#Music {mName}"
    return msg, IMG_FINAL


# --------------------------------------
# Calendar
# --------------------------------------


def buildCalendarGrid(start, end):
    calendar_counts = {}
    tracks = getRecentTracksTimestamp(start, end)
    first_week = 0
    max = -1
    maxDay = 1
    for ts in tracks:
        day = ts.day
        count = calendar_counts.get(day, 0) + 1
        calendar_counts[day] = count
        if count > max:
            max = count
            maxDay = day

    grid = [[0 for _ in range(7)] for _ in range(5)]
    TZ = timezone("Asia/Kolkata")
    first_week = 0
    s = start
    e = end
    dayseconds = 60 * 60 * 24
    while s < e:
        dt = datetime.fromtimestamp(s, tz=TZ)
        day = dt.day
        week = int(dt.strftime("%U"))
        if not first_week:
            first_week = week

        count = calendar_counts.get(day, 0)
        week_arr = (week - first_week) % 5
        weekday = int(dt.strftime("%w"))
        isMax = dt.day == maxDay
        grid[week_arr][weekday] = {"d": dt.day, "c": count, "m": isMax}
        s += dayseconds

    print("LOG: Calendar grid built")
    return grid


def buildCalendar(mLabel: str, timeSpent: str,percentage:str, grid: list):
    CLR_YELLOW = "#fff435"
    CLR_BLUE = "#8cdcfe"
    CLR_RED = "#ff0100"

    BG = Image.open(IMG_CALENDAR_TEMP)
    draw = ImageDraw.Draw(BG)

    dayFont = ImageFont.truetype(FONT_ROBOTO_SEMI_BOLD, 35)
    day_y_init = 103
    day_y_skip = 0

    countFont = ImageFont.truetype(FONT_ROBOTO_SEMI_BOLD, 50)
    count_y_init = 140
    count_y_skip = 0

    for week in grid:
        day_x_init = 90
        day_x_skip = -100
        day_y_skip += 100

        count_x_init = 51
        count_x_skip = -100
        count_y_skip += 100
        for weekday in week:
            day_x_skip += 100
            count_x_skip += 100
            info = weekday
            if not info:
                continue
            day = str(info["d"])
            count = str(info["c"])
            isMax = info["m"]

            textContent = {"text": day, "font": dayFont}
            bbox = draw.textbbox((0, 0), **textContent)
            aligned_x = day_x_init + day_x_skip - (bbox[2] - bbox[0])
            aligned_y = day_y_init + day_y_skip
            draw.text((aligned_x, aligned_y), **textContent)

            textContent = {"text": count, "font": countFont}
            bbox = draw.textbbox((0, 0), **textContent)
            aligned_x = count_x_init + count_x_skip - ((bbox[2] - bbox[0]) // 2)
            aligned_y = count_y_init + count_y_skip
            fill = CLR_BLUE if int(count) else CLR_RED
            fill = CLR_YELLOW if isMax else fill
            draw.text((aligned_x, aligned_y), **textContent, fill=fill)

    monthLabelFont = ImageFont.truetype(FONT_ROBOTO_SEMI_BOLD, 80)
    draw.text((0, 0), text=mLabel, font=monthLabelFont)
    draw.text((123, 716), text=timeSpent, font=dayFont, fill=CLR_YELLOW)
    draw.text((225, 767), text=percentage, font=dayFont, fill=CLR_YELLOW)

    BG.save(IMG_CALENDAR, optimize=True)
    print("LOG: Calendar built")
    # BG.show()


def buildMonthlyCalendar():
    start, end = getMonthlyTimestamps()

    mName, mDays = monthLabel(start, end)
    timeSpent = getDurationSpent(start, end)
    tsLabel,percentage = timeSpentLabel(end, timeSpent)

    grid = buildCalendarGrid(start, end)
    buildCalendar(mName, tsLabel,percentage ,grid)
    return IMG_CALENDAR
