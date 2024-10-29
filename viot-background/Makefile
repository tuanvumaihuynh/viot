sqlc:
	sqlc generate

test:
	go test -v -cover -short ./...

server:
	go run cmd/main.go

mock:
	mockery --name=Store --dir=./db/repository --output=./db/mock --outpkg=mockdb --case=underscore

.PHONY: sqlc test server mock
