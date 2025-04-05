# Social Media Platform Simulator

A comprehensive social media platform simulator with user behavior modeling, content interaction simulation, ad auction system, and content moderation.

## Features

### Core Simulation
- User behavior simulation with realistic engagement patterns
- Content interaction modeling (views, likes, shares, comments)
- Ad auction system with CTR prediction
- Network growth and user churn simulation
- Content moderation and reporting system

### Data Models
- User profiles and preferences
- User metrics (engagement, scroll depth, watch time)
- User network metrics (followers, following, influence)
- User relationships (follow, block, mute)
- Content types (threads, videos, mixed)
- Engagement tracking
- Ad management
- Session analytics
- Content moderation

### Machine Learning Models
- Content Interaction Prediction
- Feed Ranking
- Click-Through Rate (CTR) Prediction
  - User metrics features
  - Network metrics features
  - Content moderation features
  - Time-based features
- Feature importance tracking
- Hyperparameter tuning

### API Endpoints
- User management
  - Basic profile operations
  - User metrics
  - Network metrics
  - Relationships
  - Churn events
- Content operations
- Ad serving
- Interaction tracking
- Moderation actions
- Analytics and metrics

### Frontend Dashboard
- Real-time metrics visualization
- User analytics
  - Engagement metrics
  - Network metrics
  - Relationship graphs
  - Churn analysis
- Content performance
- Ad performance
- Moderation overview
- Network analytics

## Project Structure

```
.
├── api/
│   ├── app.py                  # Flask application entry point
│   ├── routes.py               # API endpoints and route handlers
│   ├── database.py             # Database connection and operations
│   ├── models/                 # API-specific models
│   │   ├── user.py             # User model
│   │   ├── content.py          # Content model
│   │   ├── ad.py               # Ad model
│   │   └── moderation.py       # Moderation model
│   └── utils/                  # API utilities
│       ├── auth.py             # Authentication utilities
│       ├── validation.py       # Request validation
│       └── error_handlers.py   # Error handling
├── models/
│   ├── train_models.py         # ML model training
│   ├── content_interaction.py  # Content interaction model
│   ├── feed_ranking.py         # Feed ranking model
│   ├── ctr_model.py            # Click-through rate model
│   └── utils/                  # Model utilities
│       ├── feature_engineering.py  # Feature engineering
│       ├── data_preprocessing.py   # Data preprocessing
│       └── evaluation.py           # Model evaluation
├── simulator/
│   ├── simulation.go           # Core simulation logic
│   ├── generate.go             # Data generation
│   ├── network.go              # Network simulation
│   ├── db_operations.go        # Database operations
│   ├── predictions.go          # Model predictions
│   ├── config.go               # Configuration
│   ├── errors.go               # Error handling
│   ├── logger.go               # Logging
│   ├── metrics.go              # Metrics tracking
│   ├── types.go                # Data structures
│   ├── constants.go            # Constants
│   └── utils.go                # Utilities
├── frontend/
│   ├── public/                 # Static files
│   │   ├── index.html          # HTML entry point
│   │   └── assets/             # Static assets
│   └── src/
│       ├── App.js              # React application
│       ├── index.js            # React entry point
│       ├── components/         # React components
│       │   ├── Dashboard/      # Dashboard components
│       │   ├── Users/          # User components
│       │   ├── Content/        # Content components
│       │   ├── Ads/            # Ad components
│       │   ├── Interactions/   # Interaction components
│       │   └── Moderation/     # Moderation components
│       ├── services/           # API services
│       │   ├── api.js          # API client
│       │   ├── auth.js         # Authentication service
│       │   └── data.js         # Data service
│       ├── utils/              # Frontend utilities
│       │   ├── charts.js       # Chart utilities
│       │   ├── formatters.js   # Data formatters
│       │   └── validators.js   # Form validators
│       └── styles/             # CSS styles
│           ├── global.css      # Global styles
│           └── components/     # Component styles
├── init.sql                    # Database schema
├── requirements.txt            # Python dependencies
├── package.json                # Node.js dependencies
├── go.mod                      # Go dependencies
└── README.md                   # Project documentation
```

## Setup

### Prerequisites
- Python 3.8+
- Go 1.16+
- Node.js 14+
- PostgreSQL 12+

### Database Setup
1. Create a PostgreSQL database
2. Run the schema initialization:
```bash
psql -d your_database_name -f init.sql
```

### Backend Setup
1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Go dependencies:
```bash
go mod download
```

3. Set environment variables:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
export API_PORT=5000
export MODEL_PATH="./models"
```

### Frontend Setup
1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

## Running the Application

1. Start the API server:
```bash
python api/app.py
```

2. Start the simulator:
```bash
go run simulator/simulation.go
```

3. Access the dashboard at `http://localhost:3000`

## API Documentation

### User Endpoints
- `GET /api/users` - Get all users
- `GET /api/users/{user_id}` - Get user by ID
- `GET /api/users/{user_id}/preferences` - Get user preferences
- `GET /api/users/{user_id}/metrics` - Get user engagement metrics
- `GET /api/users/{user_id}/network-metrics` - Get user network metrics
- `GET /api/users/{user_id}/relationships` - Get user relationships
- `GET /api/users/{user_id}/churn-events` - Get user churn events
- `POST /api/users` - Create a new user
- `PUT /api/users/{user_id}` - Update user
- `PUT /api/users/{user_id}/preferences` - Update user preferences
- `DELETE /api/users/{user_id}` - Delete user

### Content Endpoints
- `GET /api/content` - Get all content
- `GET /api/content/{content_id}` - Get content by ID
- `GET /api/content/threads` - Get all threads
- `GET /api/content/videos` - Get all videos
- `GET /api/content/mixed` - Get mixed content
- `GET /api/content/{content_id}/interactions` - Get content interactions
- `GET /api/content/{content_id}/recommendations` - Get content recommendations
- `GET /api/content-reports` - Get content reports
- `GET /api/content-reports/{report_id}` - Get report by ID
- `GET /api/content-flags` - Get content flags
- `GET /api/content-flags/{flag_id}` - Get flag by ID
- `POST /api/content` - Create new content
- `POST /api/content/{content_id}/interactions` - Record content interaction
- `POST /api/content/reports` - Submit content report
- `POST /api/content/flags` - Flag content
- `PUT /api/content/{content_id}` - Update content
- `DELETE /api/content/{content_id}` - Delete content

### Ad Endpoints
- `GET /api/ads` - Get all ads
- `GET /api/ads/{ad_id}` - Get ad by ID
- `GET /api/ads/{ad_id}/impressions` - Get ad impressions
- `GET /api/ads/{ad_id}/auction-logs` - Get ad auction logs
- `GET /api/ads/categories` - Get ad categories
- `POST /api/ads` - Create new ad
- `POST /api/ads/{ad_id}/impressions` - Record ad impression
- `POST /api/predict/ctr` - Predict click-through rate
- `PUT /api/ads/{ad_id}` - Update ad
- `DELETE /api/ads/{ad_id}` - Delete ad

### Interaction Endpoints
- `GET /api/interactions` - Get content interactions
- `GET /api/interactions/{interaction_id}` - Get interaction by ID
- `GET /api/feed-interactions` - Get feed interactions
- `GET /api/feed-interactions/{interaction_id}` - Get feed interaction by ID
- `GET /api/user-sessions` - Get user sessions
- `GET /api/user-sessions/{session_id}` - Get session by ID
- `POST /api/interactions` - Record content interaction
- `POST /api/feed-interactions` - Record feed interaction
- `POST /api/user-sessions` - Record user session

### Moderation Endpoints
- `GET /api/moderation-actions` - Get moderation actions
- `GET /api/moderation-actions/{action_id}` - Get action by ID
- `GET /api/content/reports` - Get content reports
- `GET /api/content/reports/{report_id}` - Get report by ID
- `GET /api/content/flags` - Get content flags
- `GET /api/content/flags/{flag_id}` - Get flag by ID
- `POST /api/content/report` - Report content
- `POST /api/content/moderate` - Moderate content
- `POST /api/content/flag` - Flag content
- `PUT /api/moderation-actions/{action_id}` - Update moderation action
- `PUT /api/content/reports/{report_id}` - Update report status

### Analytics Endpoints
- `GET /api/analytics/users` - Get user analytics
- `GET /api/analytics/content` - Get content analytics
- `GET /api/analytics/ads` - Get ad analytics
- `GET /api/analytics/interactions` - Get interaction analytics
- `GET /api/analytics/moderation` - Get moderation analytics
- `GET /api/analytics/network` - Get network analytics
- `GET /api/analytics/churn` - Get churn analytics
- `GET /api/analytics/engagement` - Get engagement analytics
- `GET /api/analytics/recommendations` - Get recommendation analytics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 