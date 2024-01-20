from wyvern.data import ALL_HISTORICAL, RASSAM_CORRELATIONS

# calculate average of S_wet / S_ref

historical = RASSAM_CORRELATIONS

s_wet = historical["Total Wetted Area, m"]
s_ref = historical["Wing Area m^2"]

s_wet_s_ref = s_wet / s_ref

print(s_wet_s_ref.mean())
