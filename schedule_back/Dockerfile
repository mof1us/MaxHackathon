FROM golang:1.25 AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o MAX-schedule ./cmd/schedulesvc/main.go


FROM alpine:3.20

WORKDIR /app

COPY --from=builder /app/MAX-schedule .

RUN mkdir -p /config/prod
COPY config/prod/prod.yaml /config/prod/prod.yaml

EXPOSE 8010
CMD ["./MAX-schedule"]
