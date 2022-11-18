// Handles POST requests
function do_json_post(body, url, is_async) {
    if (url == undefined) { return }
    if (is_async == undefined) { is_async = true }

    body = JSON.stringify(body)

    return $.ajax({
        url: url,
        type: "POST",
        async: is_async,
        data: body,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        cache : false
    });
}

// functions = [["db_function0", arg0, arg1], ["db_function1", arg0], ...]
async function query_db(functions, callback, url) {
    if (callback == undefined) { return }
    if (url == undefined) { url = "/" }

    try {
        do_json_post(functions, "/query").then(callback)
    } catch(err) {
        alert(err)
    }
}