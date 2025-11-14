package config

import (
	"flag"
	"os"

	"github.com/ilyakaznacheev/cleanenv"
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

	path := fetchConfigPath()
	if path == "" {
		panic("config path is not provided")
	}
	var cfg Config

	if err := cleanenv.ReadConfig(path, &cfg); err != nil {
		panic(err)
	}
	if err := cleanenv.UpdateEnv(&cfg); err != nil {
		panic(err)
	}

	return &cfg
}
