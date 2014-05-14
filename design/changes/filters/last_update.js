function(doc, req) {
    
    if (doc.last_update != "[CLUSTER]") {
        return true;
    } else {
    	return false;
    }

}