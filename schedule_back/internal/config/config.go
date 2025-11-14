package config

import (
	"flag"
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	Env   string   `yaml:"env"`
	HTTPS HTTP     `yaml:"http"`
	DB    DBConfig `yaml:"db"`
}

type DBConfig struct {
	Host     string `yaml:"host" env:"DB_HOST"`
	Name     string `yaml:"name"`
	User     string `yaml:"user"`
	Password string `yaml:"password"`
	SSLMode  string `yaml:"sslmode"`
	Port     string `yaml:"port" env:"DB_PORT"`
	Driver   string `yaml:"driver"`
}

type HTTP struct {
	Port string `yaml:"port"`
	Host string `yaml:"host"`
}

func fetchConfigPath() string {
	var res string

	flag.StringVar(&res, "config", "", "path to config file")
	flag.Parse()
	if res == "" {
		res = os.Getenv("CONFIG_PATH")
	}
	return res
}

func MustLoad() *Config {
	_ = godotenv.Load()
	dbConfig := DBConfig{
		Host:     os.Getenv("DB_HOST"),
		Name:     os.Getenv("DB_NAME"),
		User:     os.Getenv("DB_USER"),
		Password: os.Getenv("DB_PASSWORD"),
		SSLMode:  os.Getenv("DB_SSLMODE"),
		Port:     os.Getenv("DB_PORT"),
		Driver:   os.Getenv("DB_DRIVER"),
	}
	httpConfig := HTTP{
		Port: os.Getenv("HTTP_PORT"),
		Host: os.Getenv("HTTP_HOST"),
	}
	cfg := Config{
		Env:   os.Getenv("ENVIRONMENT"),
		HTTPS: httpConfig,
		DB:    dbConfig,
	}

	return &cfg
}
