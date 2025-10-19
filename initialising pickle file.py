import pickle

# Write the data to the pickle file
pickle.dump("", open("ProductivitySaveData.pkl", "wb"))

# Now, read the data from the pickle file
stuff = pickle.load(open("ProductivitySaveData.pkl", "rb"))

print(stuff) #to check it worked.
