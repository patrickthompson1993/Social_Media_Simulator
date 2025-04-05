-- USERS
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    age INT,
    gender TEXT,
    eye_color TEXT,
    hair_color TEXT,
    weight INT,
    skin_tone TEXT,
    political_leaning TEXT,
    region TEXT,
    device TEXT,
    persona_id INT,
    satisfaction_score FLOAT DEFAULT 1.0,
    status TEXT CHECK (status IN ('active', 'inactive', 'suspended', 'deleted')) DEFAULT 'active',
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- USER PREFERENCES
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    notification_settings JSONB,
    privacy_settings JSONB,
    content_preferences JSONB,
    language_preference TEXT,
    theme_preference TEXT,
    timezone TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- POSTS (Base table for all content types)
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    content_type TEXT CHECK (content_type IN ('thread', 'video', 'mixed')),
    content TEXT,
    topic TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- THREADS (for Twitter-like posts)
CREATE TABLE threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES posts(id),
    parent_thread_id UUID REFERENCES threads(id),
    is_thread_start BOOLEAN DEFAULT FALSE,
    thread_position INT,
    reply_count INT DEFAULT 0,
    retweet_count INT DEFAULT 0,
    quote_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- VIDEOS (for TikTok-like FYP)
CREATE TABLE videos (
    post_id UUID PRIMARY KEY REFERENCES posts(id),
    duration_seconds INT,
    resolution TEXT,
    thumbnail_url TEXT,
    video_url TEXT,
    sound_url TEXT,
    is_muted BOOLEAN DEFAULT FALSE,
    completion_rate FLOAT DEFAULT 0.0,
    watch_time_seconds INT DEFAULT 0,
    loop_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ENGAGEMENT LOGS (Likes, Shares, Comments, Bookmarks)
CREATE TABLE post_engagements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    post_id UUID REFERENCES posts(id),
    engagement_type TEXT CHECK (engagement_type IN ('like', 'share', 'comment', 'bookmark', 'retweet', 'quote')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DETAILED CONTENT INTERACTIONS
CREATE TABLE content_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    post_id UUID REFERENCES posts(id),
    interaction_type TEXT CHECK (interaction_type IN ('view', 'pause', 'resume', 'scroll_pause', 'hover', 'click', 'copy_text', 'report', 'swipe', 'sound_toggle')),
    interaction_value JSONB,
    time_spent_seconds INT,
    scroll_position INT,
    viewport_position JSONB,
    device_orientation JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FEED INTERACTIONS
CREATE TABLE feed_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    feed_type TEXT CHECK (feed_type IN ('thread', 'fyp', 'mixed')),
    post_id UUID REFERENCES posts(id),
    position INT,
    time_spent_seconds INT,
    interaction_type TEXT CHECK (interaction_type IN ('view', 'scroll', 'swipe', 'pause', 'resume')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ADS
CREATE TABLE ads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    advertiser_id UUID,
    title TEXT,
    ad_category INT,
    content TEXT,
    content_type TEXT CHECK (content_type IN ('thread', 'video', 'mixed')),
    budget FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AD IMPRESSIONS (winning ads served to users)
CREATE TABLE ad_impressions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ad_id UUID REFERENCES ads(id),
    user_id UUID REFERENCES users(id),
    feed_position INT,
    feed_type TEXT CHECK (feed_type IN ('thread', 'fyp', 'mixed')),
    predicted_ctr FLOAT,
    actual_click BOOLEAN,
    price_paid FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CTR MODEL TRAINING LOG
CREATE TABLE ad_auction_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ad_id UUID REFERENCES ads(id),
    user_id UUID REFERENCES users(id),
    feed_position INT,
    feed_type TEXT CHECK (feed_type IN ('thread', 'fyp', 'mixed')),
    predicted_ctr FLOAT,
    actual_click BOOLEAN,
    price_paid FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SESSION TRACKING (time spent, video watch %, scrolls, etc.)
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_length_seconds INT,
    avg_scroll_depth FLOAT,
    avg_watch_time FLOAT,
    feed_type TEXT CHECK (feed_type IN ('thread', 'fyp', 'mixed')),
    clicks INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- USER RELATIONSHIPS
CREATE TABLE user_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    follower_id UUID REFERENCES users(id),
    following_id UUID REFERENCES users(id),
    relationship_type TEXT CHECK (relationship_type IN ('follow', 'block', 'mute')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(follower_id, following_id, relationship_type)
);

-- USER NETWORK METRICS
CREATE TABLE user_network_metrics (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    follower_count INT DEFAULT 0,
    following_count INT DEFAULT 0,
    engagement_rate FLOAT DEFAULT 0.0,
    network_density FLOAT DEFAULT 0.0,
    influence_score FLOAT DEFAULT 0.0,
    community_clusters JSONB,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- USER METRICS
CREATE TABLE user_metrics (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    avg_scroll_depth FLOAT DEFAULT 0.0,
    avg_watch_time FLOAT DEFAULT 0.0,
    clicks_last_24h INT DEFAULT 0,
    content_interactions INT DEFAULT 0,
    video_completion_rate FLOAT DEFAULT 0.0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CHURN TRACKING (who leaves, why, etc.)
CREATE TABLE churn_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    reason TEXT,
    satisfaction_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CONTENT RECOMMENDATIONS
CREATE TABLE content_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    post_id UUID REFERENCES posts(id),
    feed_type TEXT CHECK (feed_type IN ('thread', 'fyp', 'mixed')),
    recommendation_source TEXT,
    recommendation_score FLOAT,
    recommendation_reason JSONB,
    was_shown BOOLEAN DEFAULT FALSE,
    was_engaged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- USER FEEDBACK
CREATE TABLE user_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    feedback_type TEXT CHECK (feedback_type IN ('content_quality', 'app_performance', 'feature_request', 'bug_report', 'other')),
    feedback_content TEXT,
    sentiment_score FLOAT,
    priority_score FLOAT,
    status TEXT CHECK (status IN ('new', 'in_progress', 'resolved', 'closed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- CONTENT MODERATION
CREATE TABLE content_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporter_id UUID REFERENCES users(id),
    content_id UUID NOT NULL,
    content_type TEXT CHECK (content_type IN ('post', 'comment', 'ad', 'thread', 'video')),
    report_reason TEXT CHECK (report_reason IN (
        'spam', 'hate_speech', 'violence', 'harassment', 'misinformation',
        'inappropriate', 'copyright', 'other'
    )),
    report_details TEXT,
    severity_score FLOAT,
    status TEXT CHECK (status IN ('pending', 'reviewing', 'resolved', 'dismissed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- MODERATION ACTIONS
CREATE TABLE moderation_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID REFERENCES content_reports(id),
    moderator_id UUID REFERENCES users(id),
    action_type TEXT CHECK (action_type IN (
        'warn', 'remove_content', 'ban_user', 'restrict_user',
        'flag_content', 'dismiss_report'
    )),
    action_details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CONTENT FLAGS
CREATE TABLE content_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID NOT NULL,
    content_type TEXT CHECK (content_type IN ('post', 'comment', 'ad', 'thread', 'video')),
    flag_type TEXT CHECK (flag_type IN (
        'auto_moderated', 'user_reported', 'admin_flagged', 'ai_flagged'
    )),
    flag_reason TEXT,
    flag_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);