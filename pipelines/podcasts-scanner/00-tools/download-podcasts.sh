#!/bin/bash

# Podcasts downloading script for the list of selected podcasts (sample):
# npx podcast-dl --include-meta --include-episode-meta --include-episode-transcripts --url <url> --out-dir './.../{{podcast_title}}'

    AFTER_DATE='2026-01-01'

# Dutch language learning podcasts up to B1/B2.

    # Zeg het in het Nederlands.
    npx -yes podcast-dl --after $AFTER_DATE --include-meta --include-episode-meta --include-episode-transcripts --url https://feeds.soundcloud.com/users/soundcloud:users:417093849/sounds.rss --out-dir './dutch/{{podcast_title}}'

    # Learn Dutch with The Dutch Online Academy.
    npx -yes podcast-dl --after $AFTER_DATE --include-meta --include-episode-meta --include-episode-transcripts --url https://feeds.buzzsprout.com/904798.rss --out-dir './dutch/{{podcast_title}}'

    # Nabu's Nederlandse podcast
    npx -yes podcast-dl --after $AFTER_DATE --include-meta --include-episode-meta --include-episode-transcripts --url https://anchor.fm/s/d8c4ab70/podcast/rss --out-dir './dutch/{{podcast_title}}'

# Investment. Markets review / analysis.

    # Macro Voices.
    npx podcast-dl --after $AFTER_DATE --include-meta --include-episode-meta --include-episode-transcripts --url https://feeds.feedburner.com/MacroVoices --out-dir './investment.analysis/{{podcast_title}}'

    # The Compound and Friends.
    npx podcast-dl --after $AFTER_DATE --include-meta --include-episode-meta --include-episode-transcripts --url https://feeds.megaphone.fm/TCP4771071679 --out-dir './investment.analysis/{{podcast_title}}'

    # The Meb Faber Show - Better Investing.
    npx podcast-dl --after $AFTER_DATE --include-meta --include-episode-meta --include-episode-transcripts --url https://feeds.megaphone.fm/TIFM6133783130 --out-dir './investment.analysis/{{podcast_title}}'


# Investment. Educational.

    # The Disciplined Traders Podcast.
    npx podcast-dl --after $AFTER_DATE --include-meta --include-episode-meta --include-episode-transcripts --url https://feeds.megaphone.fm/ADV4246219991 --out-dir './investment.educational/{{podcast_title}}'

    # The Investing for Beginners.
    npx podcast-dl --after $AFTER_DATE --include-meta --include-episode-meta --include-episode-transcripts --url https://feeds.megaphone.fm/ADV4246219991 --out-dir './investment.educational/{{podcast_title}}'

    # Invest Like the Best with Patrick O'Shaughnessy
    npx podcast-dl --after $AFTER_DATE --include-meta --include-episode-meta --include-episode-transcripts --url https://feeds.megaphone.fm/CLS2859450455 --out-dir './investment.educational/{{podcast_title}}'

    # Capital Allocators – Inside the Institutional Investment Industry
    npx podcast-dl --after $AFTER_DATE --include-meta --include-episode-meta --include-episode-transcripts --url https://tedseides.libsyn.com/rss --out-dir './investment.educational/{{podcast_title}}'

    # Excess Returns.
    npx podcast-dl --after $AFTER_DATE --include-meta --include-episode-meta --include-episode-transcripts --url https://anchor.fm/s/9a1dfac/podcast/rss --out-dir './investment.educational/{{podcast_title}}'

# Investment. Investors reviews.

    # We Study Billionaires – The Investors Podcast Network.
    npx podcast-dl --after $AFTER_DATE --include-meta --include-episode-meta --include-episode-transcripts --url https://feeds.megaphone.fm/PPLLC8974708240 --out-dir './investment.reviews/{{podcast_title}}'

    # The Acquirers Podcast.
    npx podcast-dl --after $AFTER_DATE --include-meta --include-episode-meta --include-episode-transcripts --url https://anchor.fm/s/9603714/podcast/rss --out-dir './investment.reviews/{{podcast_title}}'
