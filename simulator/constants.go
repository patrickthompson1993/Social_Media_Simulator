package main

// Content types
const (
	ContentTypePost    = "post"
	ContentTypeThread  = "thread"
	ContentTypeVideo   = "video"
	ContentTypeAd      = "ad"
)

// Report reasons
const (
	ReportReasonSpam        = "spam"
	ReportReasonHarassment  = "harassment"
	ReportReasonHate        = "hate"
	ReportReasonViolence    = "violence"
	ReportReasonCopyright   = "copyright"
	ReportReasonInappropriate = "inappropriate"
	ReportReasonOther       = "other"
)

// Moderation action types
const (
	ActionTypeRemove    = "remove"
	ActionTypeWarn      = "warn"
	ActionTypeBan       = "ban"
	ActionTypeFlag      = "flag"
	ActionTypeIgnore    = "ignore"
)

// Flag types
const (
	FlagTypeTemporary  = "temporary"
	FlagTypePermanent  = "permanent"
	FlagTypeReview     = "review"
)

// Interaction types
const (
	InteractionTypeView     = "view"
	InteractionTypeLike     = "like"
	InteractionTypeShare    = "share"
	InteractionTypeComment  = "comment"
	InteractionTypeBookmark = "bookmark"
	InteractionTypeRetweet  = "retweet"
	InteractionTypeQuote    = "quote"
)

// User status
const (
	UserStatusActive    = "active"
	UserStatusInactive  = "inactive"
	UserStatusBanned    = "banned"
)

// Ad categories
const (
	AdCategoryTechnology  = 0
	AdCategoryFashion     = 1
	AdCategoryFood        = 2
	AdCategoryTravel      = 3
	AdCategoryEntertainment = 4
	AdCategorySports      = 5
	AdCategoryHealth      = 6
	AdCategoryEducation   = 7
	AdCategoryFinance     = 8
	AdCategoryOther       = 9
)

// Regions
var regions = []string{
	"North America",
	"South America",
	"Europe",
	"Asia",
	"Africa",
	"Oceania",
}

// Devices
const (
	DeviceMobile  = 0
	DeviceDesktop = 1
)

// Default values
const (
	DefaultSatisfaction     = 0.5
	DefaultEngagementRate   = 0.3
	DefaultNetworkDensity   = 0.2
	DefaultInfluenceScore   = 0.1
	DefaultScrollDepth      = 0.5
	DefaultWatchTime        = 0.3
	DefaultCompletionRate   = 0.4
	DefaultReportProbability = 0.1
	DefaultChurnProbability  = 0.01
)

// Time constants
const (
	DefaultStepInterval     = 1 * time.Second
	DefaultSimulationSteps  = 100
	DefaultFlagDuration     = 24 * time.Hour
	DefaultReportWindow     = 7 * 24 * time.Hour
)

// Database constants
const (
	DefaultDBHost     = "localhost"
	DefaultDBPort     = 5432
	DefaultDBUser     = "postgres"
	DefaultDBPassword = "postgres"
	DefaultDBName     = "socialmedia"
)

// Model endpoints
const (
	DefaultCTREndpoint         = "http://localhost:5000/predict/ctr"
	DefaultContentEndpoint     = "http://localhost:5000/predict/content"
	DefaultFeedRankingEndpoint = "http://localhost:5000/predict/feed"
)

// Logging constants
const (
	DefaultLogDir = "logs"
	LogDateFormat = "2006-01-02_15-04-05"
) 