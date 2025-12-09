import Foundation

class TrafficGenModule {

    static func execute(parameters: [String: Any]) async -> [String: Any] {
        guard let targetUrl = parameters["target_url"] as? String,
              let duration = parameters["duration"] as? Int,
              let requestsPerSecond = parameters["requests_per_second"] as? Int else {
            return ["error": "Invalid parameters"]
        }

        var totalRequests = 0
        var successful = 0
        var failed = 0

        let startTime = Date()
        let endTime = startTime.addingTimeInterval(TimeInterval(duration))

        while Date() < endTime {
            do {
                guard let url = URL(string: targetUrl) else {
                    failed += 1
                    continue
                }

                let (_, response) = try await URLSession.shared.data(from: url)
                totalRequests += 1

                if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                    successful += 1
                } else {
                    failed += 1
                }

            } catch {
                failed += 1
                totalRequests += 1
            }

            try? await Task.sleep(nanoseconds: UInt64(1_000_000_000 / requestsPerSecond))
        }

        return [
            "target_url": targetUrl,
            "total_requests": totalRequests,
            "successful": successful,
            "failed": failed,
            "duration": duration
        ]
    }
}
