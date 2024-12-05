import collections
import datetime
import pickle

import openreview
import tqdm
import tyro

import numpy as np
import matplotlib.pyplot as plt # cursed...
import matplotlib.dates as mdates
import cycler


def download_reviews():
    print("downloading...")
    client = openreview.api.OpenReviewClient(
        baseurl='https://api2.openreview.net',
    )
    submissions = client.get_all_notes(
        invitation="ICLR.cc/2025/Conference/-/Submission",
        # details='directReplies', # only top-level comments
        details='replies', # also replies to top-level comments
    )
    print("downloaded! saving...")
    with open('iclr2025.pickle', 'wb') as file:
        pickle.dump(submissions, file)
    print("done! saved to 'iclr2025.pickle'")


def analyse_review_timeline(
    debug: bool = False,
):
    print("loading forums...")
    submissions = load_reviews()
    
    print("scanning forums...")
    events = collections.defaultdict(list)
    for submission in tqdm.tqdm(submissions):
        if debug:
            number = submission.number
            title = submission.content["title"]["value"]
            tqdm.tqdm.write(f"{number:6d}: {title[:50]}")
        # log the note itself
        events[
            categorise(submission.invitations, submission.signatures)
        ].append(submission.cdate)
        # reviews and comments
        for comment in submission.details['replies']:
            # classify
            events[
                categorise(comment['invitations'], comment['signatures'])
            ].append(comment['cdate'])
    
    print("compiling timeline...")
    # make it all datetime
    event_dates = {}
    for k, ts in events.items():
        event_dates[k] = collections.Counter()
        for time_ms in ts:
            # convert from s to ms
            time = time_ms / 1000
            # convert from UTC to Anywhere on Earth
            time_aoe = time - 12 * 60 * 60
            date_aoe = datetime.date.fromtimestamp(time_aoe)
            # append to counter
            event_dates[k][date_aoe] += 1
    # find the maximum date range
    all_dates = sorted(set.union(*[set(c) for c in event_dates.values()]))
    all_dates = date_range(all_dates[0], all_dates[-1])
    # assemble the final lists for plotting
    event_hists = collections.defaultdict(list)
    for date in all_dates:
        import math
        for k in event_dates:
            count = event_dates[k][date]
            # if date == datetime.date(2024, 12, 3):
            #     count = 0
            event_hists[k].append(count if count else None)

    print("plotting timeline...")
    special_times_aoe = {
        'submission open':                  datetime.date(2024,  9, 13),
        'abstract submission deadline':     datetime.date(2024,  9, 27),
        'full paper submission deadline':   datetime.date(2024, 10,  1),
        'review period begins':             datetime.date(2024, 10, 14),
        'reviews due':                      datetime.date(2024, 11,  3),
        'reviews released':                 datetime.date(2024, 11, 12),
        'revision deadline':                datetime.date(2024, 11, 27),
        'discussion deadline (reviewers)':  datetime.date(2024, 12,  2),
        '(authors)':                        datetime.date(2024, 12,  3),
        # 'meta reviews due':                 datetime.date(2024, 12, 10), # ?
        # 'final reviews due':                datetime.date(2024, 12, 10), # ?
        # 'decision notification':            datetime.date(2025,  1, 22),
    }
    plot_keys = {
        'submission by authors':            'submission',
        'official_review by reviewer':      'review',
        'official_comment by authors':      'author comment',
        'official_comment by reviewer':     'reviewer comment',
        'official_comment by ac':           'AC comment',
        'official_comment by sacs':         'SAC comment',
        'official_comment by pcs':          'PC comment',
        'public_comment by public':         'public comment',
        'desk_rejection by pcs':            'desk rejection',
        'withdrawal by authors':            'withdrawal',
        'desk_rejection_reversion by pcs':  'undo desk rejection',
        'withdrawal_reversion by pcs':      'undo withdrawal',
    }
    fig, ax = plt.subplots(figsize=(11, 4.4))
    ax.set_prop_cycle(cycler.cycler(color=[
        "#29ADFF",
        "#FFA300",
        "#FF004D",
        "#008751",
        "#C2C3C7",
        "#FFEC27",
        "#00E436",
        "#AB5236",
        "#1D2B53",
        "#7E2553",
        "#5F574F",
        "#000000",
    ]))
    for event, date in special_times_aoe.items():
        ax.vlines(date, ymin=0, ymax=13000, color='black', linestyle=':')
        ax.text(date, 13300, event, rotation=90, va='top', ha='right')
    for event, label in plot_keys.items():
        hist = event_hists[event]
        ax.semilogy(all_dates, hist, label=label, marker='.')
    fig.autofmt_xdate(rotation=15, ha='right')
    fig.subplots_adjust(bottom=0.155, top=0.86, left=0.055, right=0.995)
    ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.set_ylabel("Number of posts to OpenReview")
    ax.set_xlabel("Date (Anywhere on Earth)")
    fig.legend(loc='upper center', ncols=6)
    print("saving...")
    plt.savefig('timeline.pdf')
    print("done.")


def analyse_review_wordcount(
    debug: bool = False,
):
    print("loading forums...")
    submissions = load_reviews()
    
    print("scanning forums...")
    strings = collections.defaultdict(list)
    for submission in tqdm.tqdm(submissions):
        if debug:
            tqdm.tqdm.write(submission.content["title"]["value"][:80])
        for key in ("title", "abstract"):
            string = submission.content[key]["value"]
            strings[f"submission {key}"].append(string)
        for comment in submission.details['replies']:
            label = categorise(comment['invitations'], comment['signatures'])
            if label.startswith("official_review"):
                keys = ("summary", "strengths", "weaknesses", "questions")
            elif label.startswith("official_comment"):
                keys = ("comment",)
            else:
                if debug: tqdm.tqdm.write(f'skipping comment: {label}')
                continue
            total = ""
            for key in keys:
                string = comment['content'][key]['value']
                total += "\n\n" + string
                strings[f"{label} {key}"].append(string)
            if len(keys) > 1:
                strings[f"{label} (total)"].append(total)


    print("counting words...")
    all_wcs = {}
    for key in strings:
        print(key)
        wcs = np.array([len(s.split()) for s in strings[key]])
        print("  mean:", wcs.mean())
        print("  max: ", wcs.max())
        print("  min: ", wcs.min())
        all_wcs[key] = wcs

    print("plotting histograms...")
    print("plotting timeline...")
    fig, axes = plt.subplots(2, 5, figsize=(18, 6))
    labels = {
        "submission title":                         "submission title",
        "submission abstract":                      "submission abstract",
        "official_comment by authors comment":      "author comment",
        "official_comment by reviewer comment":     "reviewer comment",
        "official_comment by ac comment":           "AC comment",
        "official_review by reviewer summary":      "review summary",
        "official_review by reviewer strengths":    "review strengths",
        "official_review by reviewer weaknesses":   "review weaknesses",
        "official_review by reviewer questions":    "review questions",
        "official_review by reviewer (total)":      "review total",
    }
    for i, (key, label) in enumerate(labels.items()):
        counts = all_wcs[key]
        ax = axes[i//5, i%5]
        *_, bars = ax.hist(counts, bins=15)
        ax.bar_label(bars, rotation=45)
        ax.set_title(label)
        ax.set_ylim([0,45000])
    fig.tight_layout()
    fig.suptitle("Word Counts")
    fig.subplots_adjust(bottom=0.05, top=0.9, left=0.05, right=0.98)
    print("saving...")
    plt.savefig('wordcounts.pdf')
    print("done.")


# # # 
# HELPER FUNCTIONS


def parse_signatures(signatures):
    sig = signatures[0]
    if sig.startswith("~"):
        return 'public'
    base = sig.rsplit('/', maxsplit=1)[-1].lower()
    if base == "authors":
        return 'authors'
    if base.startswith('reviewer'):
        return 'reviewer'
    if base.startswith('area_chair'):
        return 'ac'
    if base == "senior_area_chairs":
        return 'sacs'
    if base == "program_chairs":
        return 'pcs'
    raise ValueError(sig)


def parse_invitations(invitations):
    return [
        i.rsplit('/', maxsplit=1)[1].lower() for i in invitations
    ][0] # sometimes there's an 'edit' afterwards, skip


def categorise(invitations, signatures):
    invite = parse_invitations(invitations)
    source = parse_signatures(signatures)
    return f"{invite} by {source}"


def load_reviews():
    with open('iclr2025.pickle', 'rb') as file:
        return pickle.load(file)


def date_range(date1, date2):
    # inclusive
    return [
        date1 + datetime.timedelta(days=n)
        for n in range((date2-date1).days + 1)
    ]


if __name__ == "__main__":
    tyro.extras.subcommand_cli_from_dict({
        "download": download_reviews,
        "timeline": analyse_review_timeline,
        "wordcount": analyse_review_wordcount,
    })
