package domain

type Token struct {
	ID    string `gorm:"primarykey"`
	Token string `gorm:"type:text;not null" json:"token"`
}
