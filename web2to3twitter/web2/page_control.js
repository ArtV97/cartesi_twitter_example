// tweet array index
const id = 0
const user = 1
const msg = 2
const timestamp = 3
const likes = 4     // integer counter
const retweets = 5  // integer counter
const replies = 6   // integer counter


let tweets_count            // total tweets
let curr_tweets_count = 0   // total tweets displayed in interface feed

let replying = {"user": null, "tweet_id": null}
let retweeting = {"user": null, "tweet_id": null}

let user_info = {   // logged user info
    "username": null,
    "join_date": null
}

function get_user_from_cookie() {
    user_info.username = null
    user_info.join_date = null

    // get cookies
    let cookie_arr = document.cookie.split("; ")

    // search for "user" cookie
    for (let i = 0; i < cookie_arr.length; i++) {
        if (cookie_arr[i].substring(0,4) == "user") {
            let info = cookie_arr[i].substring(5, cookie_arr[i].length).split(",")

            user_info.username = info[0]
            user_info.join_date = info[1]

            break
        }
    }
}

// updates page HTML according to user status (logged in or not)
function update_user() {
    let user_div_elem = document.getElementById("user")
    let user_tweet_elem = document.getElementById("user_tweet")
    
    get_user_from_cookie()

    if (!(user_info.username && user_info.join_date)) {
        user_div_elem.innerHTML = `
            <button type="button" class="btn btn-outline-dark border-0 p-0 m-0" data-bs-toggle="modal" data-bs-target="#logInModal"><u>Log in</u></button>
            to participate in the network or
            <button type="button" class="btn btn-outline-dark border-0 p-0 m-0"><u>Sign up</u></button>
        `
        user_tweet_elem.classList.add('visually-hidden')
    } else { // logged in
        user_div_elem.innerHTML = `
            <img src="user.png" class="border rounded-circle", style="height: 100px; width: 100px;">
            <div class="text-center display-inline">
                ${user_info.username}
            </div>
            <button type="button" class="btn btn-outline-dark border-0 mb-3" onclick="log_out()">Log out</button>
            <br>
            <button type="button" class="btn btn-outline-dark" data-bs-toggle="modal" data-bs-target="#tweetModal">Tweet</button>
        `

        user_tweet_elem.classList.remove('visually-hidden')
    }
}

function log_in() {
    let username = document.getElementById('username').value
    let password = document.getElementById('password').value

    let myModalEl = document.getElementById('logInModal')
    let modal = bootstrap.Modal.getInstance(myModalEl) // Returns a Bootstrap modal instance
    modal.toggle()

    query_db([ ["user_login", username, password] ], (res) => {
        if (res[0].success && res[0].result) {
            // create "user" cookie
            document.cookie = `user=${res[0].result}`

            window.location.reload()
        }
    })
}

function log_out() {
    // delete user cookie
    document.cookie = "user=; max-age=0"

    window.location.reload()
}

function post_tweet(option, element_id, model_id) {
    let post_options = {"tweet": 0, "retweet": 1, "reply": 2}

    let close_model = function() {
        if (model_id) {
            let modal_elem = document.getElementById(model_id)
            bootstrap.Modal.getInstance(modal_elem).toggle()
        }
    }

    let tweet_msg = document.getElementById(element_id).value

    switch (post_options[option]) {
        case 0:
            query_db([["create_tweet", user_info.username, tweet_msg, new Date().toUTCString()]], (res) => {
                if (res[0].success && res[0].result) {
                    console.log(`posted tweet: ${res[0].result}`)
                    close_model()
                }
            })                    
            break

        case 1:
            query_db([["generate_retweet", retweeting.tweet_id, user_info.username,
            new Date().toUTCString(), tweet_msg]], (res) => {
                if (res[0].success && res[0].result) {
                    console.log(`posted retweet: ${res[0].result}`)
                    close_model()
                }
            })
            retweeting.user = null
            retweeting.tweet_id = null
            break

        case 2:
            query_db([["generate_reply", replying.tweet_id, user_info.username,
            new Date().toUTCString(), tweet_msg]], (res) => {
                if (res[0].success && res[0].result) {
                    console.log(`posted reply: ${res[0].result}`)
                    close_model()
                }
            })
            replying.user = null
            replying.tweet_id = null
            break
        
        default:
            console.log("default")
            break
    }

    document.getElementById(element_id).value = "" // clear
}

function reply(replying_to, tweet_id) {
    if (!(user_info.username && user_info.join_date)) {
        alert("You must log in to reply tweets.")
        return
    }

    replying.user = replying_to
    replying.tweet_id = tweet_id

    document.getElementById("replying_to").innerHTML = replying_to
}

function retweet(retweeting_to, tweet_id) {
    if (!(user_info.username && user_info.join_date)) {
        alert("You must log in to retweet tweets.")
        return
    }

    retweeting.user = retweeting_to
    retweeting.tweet_id = tweet_id

    document.getElementById("retweet_to").innerHTML = retweeting_to
}

function like(tweet_id) {
    if (!(user_info.username && user_info.join_date)) {
        alert("You must log in to like tweets.")
        return
    }

    query_db([["create_like", tweet_id, user_info.username]], (res) => {
        if (res[0].success && res[0].result) {
            console.log(`Tweet ${tweet_id} like by User ${user_info.username}`)
        }
    })
}


function display_update_option() {
    let new_tweets = tweets_count - curr_tweets_count
    let update_tweets_elem = document.getElementById("update_tweets")

    update_tweets_elem.innerHTML = `
        <button type="submit" class="btn btn-outline-dark border-0 p-2" onclick="update_tweets()">
            Show new Tweets (${new_tweets})
        </button>
    `
}

function update_tweets() {
    let feed_elem = document.getElementById("feed")

    query_db([
        ["get_tweets_feed"], ["get_user_likes", user_info.username],
        ["get_user_retweets", user_info.username], ["get_user_replies", user_info.username]], (res) => {
        console.log(res)
        let tweets
        if (!res[0].success) { return } // failed to get tweets feed
        
        tweets = res[0].result
        let user_likes = res[1].success? res[1].result:[]
        let user_retweets = res[2].success? res[2].result:[]
        let user_replies = res[3].success? res[3].result:[]

        let get_btn_type = function (tweet_id, arr) {
            if (!arr.includes(tweet_id)) {
                return 'btn-outline-dark'
            }

            return 'btn-dark'
        }

        for (let i = tweets.length -1; i >= curr_tweets_count; i--) {
            let like_btn_type = get_btn_type(tweets[i][id], user_likes)
            let retweet_btn_type = get_btn_type(tweets[i][id], user_retweets)
            let reply_btn_type = get_btn_type(tweets[i][id], user_replies)


            feed_elem.innerHTML += `
                <li class="list-group-item"style="background-color: floralwhite;">
                <div class="row p-1">
                <img src="user.png" class="col-2 rounded-circle border", style="height: 75px; width: 75px;">
                <div class="col">
                <div>
                <span>${tweets[i][user]}</span>
                <i class="bi bi-dot m-1"></i>
                <span>${tweets[i][timestamp]}</span>
                </div>
                
                <div>
                <p>${tweets[i][msg]}</p>

                <button type="button" class="btn ${reply_btn_type}" onClick="reply('${tweets[i][user]}', ${tweets[i][id]})" data-bs-toggle="modal" data-bs-target="#replyModal"><i class="bi bi-chat"></i> ${tweets[i][replies]}</button>
                <button type="button" class="btn ${retweet_btn_type} mx-5" onClick="retweet('${tweets[i][user]}', ${tweets[i][id]})" data-bs-toggle="modal" data-bs-target="#retweetModal"><i class="bi bi-arrow-repeat"></i> ${tweets[i][retweets]}</button>
                <button type="button" class="btn ${like_btn_type}" onClick="like('${tweets[i][id]}')"><i class="bi bi-heart"></i> ${tweets[i][likes]}</i></button>
                
                </div>
                </div>
                </div>
                </li>
            `
        }
    
        tweets_count = tweets.length
        curr_tweets_count = tweets_count

        let update_tweets_elem = document.getElementById("update_tweets")
        update_tweets_elem.innerHTML = "" // clear
    })
}


// window.setInterval(() => {
//     query_db([ ["count_tweets_feed"] ], (res) => {
//         tweets_count = res[0]

//         if (curr_tweets_count != tweets_count) {
//             display_update_option()
//         }

//     })
// }, 10000);