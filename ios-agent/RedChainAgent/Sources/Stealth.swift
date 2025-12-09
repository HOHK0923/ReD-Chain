import Foundation
import UIKit

class StealthManager {

    static let shared = StealthManager()

    private init() {}

    /// Check if running in simulator (anti-analysis)
    func isSimulator() -> Bool {
        #if targetEnvironment(simulator)
        return true
        #else
        return false
        #endif
    }

    /// Check if device is jailbroken
    func isJailbroken() -> Bool {
        // Check for common jailbreak files
        let jailbreakPaths = [
            "/Applications/Cydia.app",
            "/Library/MobileSubstrate/MobileSubstrate.dylib",
            "/bin/bash",
            "/usr/sbin/sshd",
            "/etc/apt",
            "/private/var/lib/apt/"
        ]

        for path in jailbreakPaths {
            if FileManager.default.fileExists(atPath: path) {
                return true
            }
        }

        // Check if can write to system directory
        let testPath = "/private/jailbreak_test.txt"
        do {
            try "test".write(toFile: testPath, atomically: true, encoding: .utf8)
            try FileManager.default.removeItem(atPath: testPath)
            return true
        } catch {
            // Can't write = not jailbroken
        }

        return false
    }

    /// Check if debugger is attached
    func isDebuggerAttached() -> Bool {
        var info = kinfo_proc()
        var mib: [Int32] = [CTL_KERN, KERN_PROC, KERN_PROC_PID, getpid()]
        var size = MemoryLayout<kinfo_proc>.stride

        let result = sysctl(&mib, UInt32(mib.count), &info, &size, nil, 0)

        if result != 0 {
            return false
        }

        return (info.kp_proc.p_flag & P_TRACED) != 0
    }

    /// Get device fingerprint
    func getDeviceFingerprint() -> [String: Any] {
        let device = UIDevice.current

        return [
            "model": device.model,
            "name": device.name,
            "system_name": device.systemName,
            "system_version": device.systemVersion,
            "identifier_for_vendor": device.identifierForVendor?.uuidString ?? "unknown",
            "is_simulator": isSimulator(),
            "is_jailbroken": isJailbroken(),
            "is_debugger_attached": isDebuggerAttached()
        ]
    }

    /// Random delay for network requests (avoid pattern detection)
    func randomDelay() -> TimeInterval {
        return TimeInterval.random(in: 5...15)
    }

    /// Obfuscate strings (simple XOR)
    func obfuscate(_ string: String, key: UInt8 = 0x42) -> String {
        return String(string.utf8.map { Character(UnicodeScalar($0 ^ key)) })
    }

    func deobfuscate(_ string: String, key: UInt8 = 0x42) -> String {
        return obfuscate(string, key: key)  // XOR is symmetric
    }
}
