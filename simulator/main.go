package main

import (
	"flag"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"
)

func main() {
	// Parse command line flags
	numSteps := flag.Int("steps", 100, "Number of simulation steps to run")
	stepInterval := flag.Duration("interval", 1*time.Second, "Interval between simulation steps")
	flag.Parse()

	// Initialize database connection
	err := initDB()
	if err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}
	defer db.Close()

	// Set up signal handling for graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	// Run simulation loop
	log.Printf("Starting simulation with %d steps at %v intervals", *numSteps, *stepInterval)
	
	for i := 0; i < *numSteps; i++ {
		select {
		case <-sigChan:
			log.Println("Received shutdown signal, stopping simulation")
			return
		default:
			log.Printf("Running simulation step %d/%d", i+1, *numSteps)
			
			err := SimulateStep()
			if err != nil {
				log.Printf("Error in simulation step: %v", err)
			}
			
			time.Sleep(*stepInterval)
		}
	}
	
	log.Println("Simulation completed successfully")
}
