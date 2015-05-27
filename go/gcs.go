package main

import (
    "os"
    "fmt"
    "log"
    "io/ioutil"
//    "golang.org/x/net/context"
    "golang.org/x/oauth2"
    "golang.org/x/oauth2/google"
    storage "google.golang.org/api/storage/v1"
)

// return a Google Cloud Services connection
func getService() (*storage.Service) {
    const scope = storage.DevstorageFullControlScope

    // read in the creds
    jsonKey, err := ioutil.ReadFile("cloud_backup_secret.json")

    if err != nil {
        log.Fatalf("Unable to read file: %v", err)
    }

    config, err := google.JWTConfigFromJSON(jsonKey, "https://www.googleapis.com/auth/devstorage.read_write")

    if err != nil {
        log.Fatalf("Error configuring from JSON: %v", err)
    }

    // create the authenticated client
    httpClient := config.Client(oauth2.NoContext)

    service, err := storage.New(httpClient)

    if err != nil {
        log.Fatalf("Unable to create storage service: %v", err)
        return nil
    }

    return service
}

func main() {
    service := getService()

    if service == nil {
       os.Exit(1)
    }

    if res, err := service.Objects.List("blkdev_1").Do(); err == nil {
        fmt.Printf("Objects in bucket %v:\n", "blkdev_1")

        for _, object := range res.Items {
            fmt.Println(object.Name)
        }

        fmt.Println()
    } else {
        log.Fatalf("Objects.List failed: %v", err)
    }
}
