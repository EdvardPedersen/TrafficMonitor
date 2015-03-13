import gdbm as dbm

db = dbm.open("default.camera", 'cs')
key = db.firstkey()
while(key != None):
	print("Key: " + key + " Value: " + db[key])
	key = db.nextkey(key)