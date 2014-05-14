function(doc, req) {
    
    if (doc.last_update != "oculus001") {
        return true;
    } else {
    	return false;
    }

}