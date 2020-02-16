$(document).ready(function () {
    $.get('/my_course_views', function (result) {
        var my_views = JSON.parse(result);
        google.charts.load('current', {'packages': ['corechart']});
        google.charts.setOnLoadCallback(drawChart);

        function drawChart() {
            var data = new google.visualization.DataTable();
            data.addColumn('string', 'Topping');
            data.addColumn('number', 'Slices');
            data.addRows([
                ['Artificial inteligence', my_views[0]],
                ['Natural Language Processing', my_views[1]],
                ['Logical circuits', my_views[2]],
                ['Signals and Systems', my_views[3]],
            ]);
            var options = {
                'title': 'Pie Chart',
                'width': '100%',
                'height': '100%'
            };
            var chart = new google.visualization.PieChart(document.getElementById('pie_div'));
            chart.draw(data, options);


            var data2 = google.visualization.arrayToDataTable([
                ["Element", "Density", {role: "style"}],
                ["Artificial inteligence", my_views[0], "#b87333"],
                ["Natural Language Processing", my_views[1], "silver"],
                ["Logical circuits", my_views[2], "gold"],
                ["Signals and Systems", my_views[3], "color: #e5e4e2"]
            ]);

            var view2 = new google.visualization.DataView(data2);
            view2.setColumns([0, 1,
                {
                    calc: "stringify",
                    sourceColumn: 1,
                    type: "string",
                    role: "annotation"
                },
                2]);

            var options2 = {
                title: "Bar Chart",
                width: 600,
                height: 400,
                bar: {groupWidth: "95%"},
                legend: {position: "none"},
            };
            var chart2 = new google.visualization.ColumnChart(document.getElementById("columnchart_values"));
            chart2.draw(view2, options2);
        }
    });
});