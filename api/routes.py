from flask import Blueprint, request, jsonify
from api.models.train_models import ContentInteractionModel, FeedRankingModel, CTRModel
import json
from datetime import datetime, timedelta
from database import db

api = Blueprint('api', __name__)

# Load models
content_model = ContentInteractionModel()
content_model.load_model("models")

feed_model = FeedRankingModel()
feed_model.load_model("models")

ctr_model = CTRModel()
ctr_model.load_model("models")

@api.route('/predict/content-interaction', methods=['POST'])
def predict_content_interaction():
    data = request.json
    
    # Prepare features
    features = content_model.prepare_features(pd.DataFrame([data]))
    features_scaled = content_model.scaler.transform(features)
    
    # Get prediction
    prediction = content_model.model.predict_proba(features_scaled)[0]
    
    return jsonify({
        'interaction_probability': float(prediction[1]),
        'confidence_score': float(max(prediction)),
        'timestamp': datetime.now().isoformat()
    })

@api.route('/predict/feed-ranking', methods=['POST'])
def predict_feed_ranking():
    data = request.json
    
    # Prepare features
    features = feed_model.prepare_features(pd.DataFrame([data]))
    features_scaled = feed_model.scaler.transform(features)
    
    # Get prediction
    score = feed_model.model.predict(features_scaled)[0]
    
    return jsonify({
        'engagement_score': float(score),
        'timestamp': datetime.now().isoformat()
    })

@api.route('/predict/ctr', methods=['POST'])
def predict_ctr():
    data = request.json
    
    # Prepare features
    features = ctr_model.prepare_features(pd.DataFrame([data]))
    features_scaled = ctr_model.scaler.transform(features)
    
    # Get prediction
    prediction = ctr_model.model.predict_proba(features_scaled)[0]
    
    return jsonify({
        'click_probability': float(prediction[1]),
        'confidence_score': float(max(prediction)),
        'timestamp': datetime.now().isoformat()
    })

@api.route('/content/report', methods=['POST'])
def report_content():
    data = request.json
    
    # Validate required fields
    required_fields = ['reporter_id', 'content_id', 'content_type', 'report_reason']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Insert report
        query = """
        INSERT INTO content_reports (
            reporter_id, content_id, content_type, report_reason,
            report_details, severity_score, status, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING id
        """
        
        result = db.execute(query, (
            data['reporter_id'],
            data['content_id'],
            data['content_type'],
            data['report_reason'],
            data.get('report_details', ''),
            data.get('severity_score', 0.5),
            'pending',
            datetime.now()
        ))
        
        report_id = result.fetchone()[0]
        
        # Check for automatic moderation
        if data.get('severity_score', 0.5) > 0.8:
            # Auto-flag content
            flag_query = """
            INSERT INTO content_flags (
                content_id, content_type, flag_type,
                flag_reason, flag_score, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6)
            """
            
            db.execute(flag_query, (
                data['content_id'],
                data['content_type'],
                'auto_moderated',
                data['report_reason'],
                data.get('severity_score', 0.5),
                datetime.now()
            ))
            
            # Update report status
            db.execute(
                "UPDATE content_reports SET status = 'resolved' WHERE id = $1",
                (report_id,)
            )
        
        return jsonify({
            'report_id': report_id,
            'status': 'pending',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/content/moderate', methods=['POST'])
def moderate_content():
    data = request.json
    
    # Validate required fields
    required_fields = ['report_id', 'moderator_id', 'action_type']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Insert moderation action
        query = """
        INSERT INTO moderation_actions (
            report_id, moderator_id, action_type,
            action_details, created_at
        ) VALUES ($1, $2, $3, $4, $5)
        RETURNING id
        """
        
        result = db.execute(query, (
            data['report_id'],
            data['moderator_id'],
            data['action_type'],
            json.dumps(data.get('action_details', {})),
            datetime.now()
        ))
        
        action_id = result.fetchone()[0]
        
        # Update report status
        db.execute(
            "UPDATE content_reports SET status = 'resolved' WHERE id = $1",
            (data['report_id'],)
        )
        
        # If action is to flag content, create flag
        if data['action_type'] == 'flag_content':
            report = db.execute(
                "SELECT content_id, content_type, report_reason FROM content_reports WHERE id = $1",
                (data['report_id'],)
            ).fetchone()
            
            flag_query = """
            INSERT INTO content_flags (
                content_id, content_type, flag_type,
                flag_reason, flag_score, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6)
            """
            
            db.execute(flag_query, (
                report['content_id'],
                report['content_type'],
                'admin_flagged',
                report['report_reason'],
                data.get('flag_score', 0.5),
                datetime.now()
            ))
        
        return jsonify({
            'action_id': action_id,
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/content/flags', methods=['GET'])
def get_content_flags():
    content_id = request.args.get('content_id')
    
    try:
        query = """
        SELECT cf.*, cr.report_reason, cr.severity_score
        FROM content_flags cf
        LEFT JOIN content_reports cr ON cf.content_id = cr.content_id
        WHERE cf.content_id = $1 AND cf.expires_at > NOW()
        """
        
        flags = db.execute(query, (content_id,)).fetchall()
        
        return jsonify({
            'flags': [dict(flag) for flag in flags],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/content/reports', methods=['GET'])
def get_content_reports():
    content_id = request.args.get('content_id')
    status = request.args.get('status', 'pending')
    
    try:
        query = """
        SELECT cr.*, ma.action_type, ma.action_details
        FROM content_reports cr
        LEFT JOIN moderation_actions ma ON cr.id = ma.report_id
        WHERE cr.content_id = $1 AND cr.status = $2
        """
        
        reports = db.execute(query, (content_id, status)).fetchall()
        
        return jsonify({
            'reports': [dict(report) for report in reports],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/users', methods=['GET'])
def get_users():
    try:
        query = """
        SELECT u.*, 
               up.notification_settings,
               up.privacy_settings,
               up.content_preferences,
               unm.follower_count,
               unm.following_count,
               unm.engagement_rate,
               unm.network_density,
               unm.influence_score,
               unm.community_clusters
        FROM users u
        LEFT JOIN user_preferences up ON u.id = up.user_id
        LEFT JOIN user_network_metrics unm ON u.id = unm.user_id
        """
        users = db.execute(query)
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/content', methods=['GET'])
def get_content():
    try:
        query = """
        SELECT p.*, 
               t.reply_count,
               t.retweet_count,
               t.quote_count,
               v.duration_seconds,
               v.completion_rate,
               v.watch_time_seconds,
               COUNT(cr.id) as report_count,
               COALESCE(cf.flag_score, 0) as flag_score,
               CASE WHEN cf.id IS NOT NULL THEN 1 ELSE 0 END as has_active_flags,
               CASE 
                   WHEN ma.action_type = 'remove_content' THEN 'removed'
                   WHEN ma.action_type = 'flag_content' THEN 'flagged'
                   ELSE 'active'
               END as moderation_status
        FROM posts p
        LEFT JOIN threads t ON p.id = t.post_id
        LEFT JOIN videos v ON p.id = v.post_id
        LEFT JOIN content_reports cr ON p.id = cr.content_id
        LEFT JOIN content_flags cf ON p.id = cf.content_id
        LEFT JOIN moderation_actions ma ON cr.id = ma.report_id
        GROUP BY p.id, t.reply_count, t.retweet_count, t.quote_count,
                 v.duration_seconds, v.completion_rate, v.watch_time_seconds,
                 cf.flag_score, cf.id, ma.action_type
        """
        content = db.execute(query)
        return jsonify(content)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/ads', methods=['GET'])
def get_ads():
    try:
        query = """
        SELECT a.*, 
               ai.predicted_ctr,
               ai.actual_click,
               COUNT(cr.id) as report_count,
               COALESCE(cf.flag_score, 0) as flag_score,
               CASE WHEN cf.id IS NOT NULL THEN 1 ELSE 0 END as has_active_flags,
               CASE 
                   WHEN ma.action_type = 'remove_content' THEN 'removed'
                   WHEN ma.action_type = 'flag_content' THEN 'flagged'
                   ELSE 'active'
               END as moderation_status
        FROM ads a
        LEFT JOIN ad_impressions ai ON a.id = ai.ad_id
        LEFT JOIN content_reports cr ON a.id = cr.content_id
        LEFT JOIN content_flags cf ON a.id = cf.content_id
        LEFT JOIN moderation_actions ma ON cr.id = ma.report_id
        GROUP BY a.id, ai.predicted_ctr, ai.actual_click,
                 cf.flag_score, cf.id, ma.action_type
        """
        ads = db.execute(query)
        return jsonify(ads)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/interactions', methods=['GET'])
def get_interactions():
    try:
        query = """
        SELECT ci.*, 
               u.satisfaction_score,
               u.engagement_rate,
               u.network_density,
               u.influence_score
        FROM content_interactions ci
        JOIN users u ON ci.user_id = u.id
        """
        interactions = db.execute(query)
        return jsonify(interactions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/feed-interactions', methods=['GET'])
def get_feed_interactions():
    try:
        query = """
        SELECT fi.*, 
               us.session_length_seconds,
               us.avg_scroll_depth,
               us.avg_watch_time
        FROM feed_interactions fi
        JOIN user_sessions us ON fi.user_id = us.user_id
        """
        feed_interactions = db.execute(query)
        return jsonify(feed_interactions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/content-reports', methods=['GET'])
def get_content_reports():
    try:
        query = """
        SELECT cr.*, 
               ma.action_type,
               ma.action_details
        FROM content_reports cr
        LEFT JOIN moderation_actions ma ON cr.id = ma.report_id
        """
        reports = db.execute(query)
        return jsonify(reports)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/moderation-actions', methods=['GET'])
def get_moderation_actions():
    try:
        query = """
        SELECT ma.*, 
               cr.content_id,
               cr.report_reason
        FROM moderation_actions ma
        JOIN content_reports cr ON ma.report_id = cr.id
        """
        actions = db.execute(query)
        return jsonify(actions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/content-flags', methods=['GET'])
def get_content_flags():
    try:
        query = """
        SELECT cf.*, 
               cr.report_reason,
               cr.severity_score
        FROM content_flags cf
        LEFT JOIN content_reports cr ON cf.content_id = cr.content_id
        """
        flags = db.execute(query)
        return jsonify(flags)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/user-sessions', methods=['GET'])
def get_user_sessions():
    try:
        query = """
        SELECT us.*, 
               u.satisfaction_score,
               u.engagement_rate
        FROM user_sessions us
        JOIN users u ON us.user_id = u.id
        """
        sessions = db.execute(query)
        return jsonify(sessions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/user-preferences', methods=['GET'])
def get_user_preferences():
    try:
        query = """
        SELECT up.*, 
               u.satisfaction_score,
               u.engagement_rate
        FROM user_preferences up
        JOIN users u ON up.user_id = u.id
        """
        preferences = db.execute(query)
        return jsonify(preferences)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/users/{user_id}/metrics', methods=['GET'])
def get_user_metrics():
    user_id = request.view_args['user_id']
    
    try:
        # Get user metrics
        metrics = db.execute("""
            SELECT 
                um.avg_scroll_depth,
                um.avg_watch_time,
                um.clicks_last_24h,
                um.content_interactions,
                um.video_completion_rate,
                um.last_updated
            FROM user_metrics um
            WHERE um.user_id = $1
        """, (user_id,)).fetchone()
        
        if not metrics:
            return jsonify({'error': 'User metrics not found'}), 404
            
        return jsonify({
            'avg_scroll_depth': float(metrics['avg_scroll_depth']),
            'avg_watch_time': float(metrics['avg_watch_time']),
            'clicks_last_24h': int(metrics['clicks_last_24h']),
            'content_interactions': int(metrics['content_interactions']),
            'video_completion_rate': float(metrics['video_completion_rate']),
            'last_updated': metrics['last_updated'].isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/users/{user_id}/network-metrics', methods=['GET'])
def get_user_network_metrics():
    user_id = request.view_args['user_id']
    
    try:
        # Get user network metrics
        metrics = db.execute("""
            SELECT 
                unm.follower_count,
                unm.following_count,
                unm.engagement_rate,
                unm.network_density,
                unm.influence_score,
                unm.community_clusters,
                unm.last_updated
            FROM user_network_metrics unm
            WHERE unm.user_id = $1
        """, (user_id,)).fetchone()
        
        if not metrics:
            return jsonify({'error': 'User network metrics not found'}), 404
            
        return jsonify({
            'follower_count': int(metrics['follower_count']),
            'following_count': int(metrics['following_count']),
            'engagement_rate': float(metrics['engagement_rate']),
            'network_density': float(metrics['network_density']),
            'influence_score': float(metrics['influence_score']),
            'community_clusters': metrics['community_clusters'],
            'last_updated': metrics['last_updated'].isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/users/{user_id}/relationships', methods=['GET'])
def get_user_relationships():
    user_id = request.view_args['user_id']
    relationship_type = request.args.get('type', 'follow')
    
    try:
        # Get user relationships
        relationships = db.execute("""
            SELECT 
                ur.id,
                ur.follower_id,
                ur.following_id,
                ur.relationship_type,
                ur.created_at
            FROM user_relationships ur
            WHERE (ur.follower_id = $1 OR ur.following_id = $1)
            AND ur.relationship_type = $2
        """, (user_id, relationship_type)).fetchall()
        
        return jsonify([{
            'id': str(r['id']),
            'follower_id': str(r['follower_id']),
            'following_id': str(r['following_id']),
            'relationship_type': r['relationship_type'],
            'created_at': r['created_at'].isoformat()
        } for r in relationships])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/users/{user_id}/churn-events', methods=['GET'])
def get_user_churn_events():
    user_id = request.view_args['user_id']
    
    try:
        # Get user churn events
        events = db.execute("""
            SELECT 
                ce.id,
                ce.reason,
                ce.satisfaction_score,
                ce.created_at
            FROM churn_events ce
            WHERE ce.user_id = $1
            ORDER BY ce.created_at DESC
        """, (user_id,)).fetchall()
        
        return jsonify([{
            'id': str(e['id']),
            'reason': e['reason'],
            'satisfaction_score': float(e['satisfaction_score']),
            'created_at': e['created_at'].isoformat()
        } for e in events])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/content-recommendations', methods=['GET'])
def get_content_recommendations():
    try:
        query = """
        SELECT cr.*, 
               p.content_type,
               p.engagement_rate
        FROM content_recommendations cr
        JOIN posts p ON cr.content_id = p.id
        """
        recommendations = db.execute(query)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/user-feedback', methods=['GET'])
def get_user_feedback():
    try:
        query = """
        SELECT uf.*, 
               u.satisfaction_score,
               u.engagement_rate
        FROM user_feedback uf
        JOIN users u ON uf.user_id = u.id
        """
        feedback = db.execute(query)
        return jsonify(feedback)
    except Exception as e:
        return jsonify({'error': str(e)}), 500 