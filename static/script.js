function setFormError(v) {
    if (v) {
        $("form").addClass("has-error").addClass("has-feedback");
        $(".input-error-message").text(v);
    } else {
        $("form").removeClass("has-error").removeClass("has-feedback");
    }
}

function addScan(data) {
    sitemap_id = parseInt(data.id);
    domains = data.domains.join(", ");
    started = data.started;
    status = data.status;

    watch_tasks[sitemap_id] = true;

    // Set the output display
    var out = $("<div class='output' data-task-id='" + sitemap_id + "'></div>");

    outt = '';

    outt += "Domains: <pre class='task-domains'>" + domains + "</pre><br>";
    outt += "Queued: <pre class='task-started'>" + started + "</pre><br>";
    outt += "Status: <pre class='task-status'>" + status + "</pre>";

    out.html(outt);

    $("#output").prepend(out);
}

function loadHistory() {
    $.ajax({
        type: 'GET',
        url: 'api/history',
        dataType: 'json',
        success: function(data) {
            for (var idx in data) {
                addScan(data[idx]);
            }
        }
    });
}

function checkForUpdates() {
    // Do the updating
    for (var id in watch_tasks) {
        if (!watch_tasks[id]) {
            delete watch_tasks[id];
        }
    }

    var ids = [];
    for (var id in watch_tasks) ids.push(parseInt(id));

    if (ids.length > 0) {
        // Do the update
        $.ajax({
            type: 'POST',
            url: 'api/status',
            dataType: 'json',
            data: JSON.stringify({task_ids:ids}),
            processData: false,
            success: function(data) {
                for (var id in data) {
                    var sm = data[id];

                    $("div.output").each(function() {
                        if ($(this).data('task-id') == sm.id) {

                            $(this).children("pre.task-status").text(sm.status);

                            if ($(this).children("pre.task-crawl-started").length == 0 && sm.crawl_started !== undefined) {
                                $(this).html($(this).html() + '<br>Crawl Started: <pre class="task-crawl-started">' + sm.crawl_started + '</pre>');
                            }

                            if ($(this).children("pre.task-crawl-ended").length == 0 && sm.crawl_ended !== undefined) {
                                $(this).html($(this).html() + '<br>Crawl Ended: <pre class="task-crawl-ended">' + sm.crawl_ended + '</pre>');
                            }

                            if (sm.crawl_ended !== undefined || sm.status == 'finished' || sm.status == 'page_limit') {
                                watch_tasks[sm.id] = false;
                            }

                            if (sm.status.indexOf('finished') != -1 || sm.status.indexOf('page_limit') != -1) {
                                $(this).html($(this).html() + '<br><a href="download/' + sm.id + '" class="btn btn-info">Download Sitemap</a>');
                            }

                            if (sm.errors.length > 0) {
                                for (var idx in sm.errors) {
                                    var error = sm.errors[idx];
                                    var code = $("<code></code>");
                                    code.text(error['name']);
                                    if (error['details'] != '') {
                                        code.text(code.text() + ": " + error['details']);
                                    }
                                    $(this).append(code);
                                }
                            }

                        }
                    });

                }
            },
            error: function(xhr, textStatus, errorThrown) {
                setFormError("Failed to update tasks!");
            }
        });
    }
}

(function($) {
    $(document).ready(function() {
        watch_tasks = {};
        setInterval(checkForUpdates, 1000);

        loadHistory();

        $("form").submit(function(e) {
            e.preventDefault();
            setFormError(false);

            var domains = $("input[name=domains]").val();

            if (domains.trim().length <= 0) {
                setFormError("You must enter a valid list of domains!");
                return;
            }

            domains = domains.split(/[\s,]+/);

            // Filter domains
            for (var i=0; i<domains.length; i++) {
                var d = domains[i];

                d = d.replace('https://', '').replace('http://', '');
                d = d.split('/')[0];

                if (d.indexOf("www.") === 0) {
                    d = d.substring(4);
                }

                domains[i] = d;
            }

            var nd = [];
            for (var d in domains) {
                var has = false;

                // Skip if no period
                if (domains[d].indexOf(".") == -1) {
                    has = true;
                }

                // Check for dupes
                for (var d2 in nd) {
                    if (nd[d2] == domains[d]) {
                        has = true;
                    }
                }
                if (!has) {
                    nd.push(domains[d]);
                }
            }
            domains = nd;

            if (domains.length <= 0) {
                setFormError("You must enter a valid list of domains!");
                return;
            }

            $("input[name=domains]").val(domains.join(", "));

            var value = JSON.stringify({domains: domains});

            $.ajax({
                type: 'POST',
                url: 'api/start',
                dataType: 'json',
                data: value,
                success: function(data) {
                    addScan(data);
                },
                error: function(xhr, textStatus, errorThrown) {
                    if (xhr.status == 400) {
                        // Bad request!
                        setFormError(true);
                    }
                    console.log(xhr.status);
                    console.log(textStatus);
                    console.log(errorThrown);
                }
            });

        });

    });
})(jQuery);
