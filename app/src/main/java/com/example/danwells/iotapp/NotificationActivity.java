package com.example.danwells.iotapp;

import android.content.Intent;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.design.widget.BottomNavigationView;
import android.support.v7.app.AppCompatActivity;
import android.view.MenuItem;
import android.widget.ListView;
import android.widget.Toast;

public class NotificationActivity extends AppCompatActivity {

    private ListView listView;
    private CustomAdapter adapter;
    String[] nameList = {"David", "Sally", "David", "Steven"};
    String[] timeList = {"5 mins ago", "45 mins ago", "1 hour ago", "1 day ago"};
    String[] actionList = {"arrived", "departed", "arrived", "arrived"};
    BottomNavigationView navigation;
    Bundle savedState;

    private BottomNavigationView.OnNavigationItemSelectedListener mOnNavigationItemSelectedListener
            = new BottomNavigationView.OnNavigationItemSelectedListener() {

        @Override
        public boolean onNavigationItemSelected(@NonNull MenuItem item) {
            switch (item.getItemId()) {
                case R.id.navigation_refresh:
                    refresh();
                    return true;
                case R.id.navigation_dashboard:
                    startActivity(new Intent(NotificationActivity.this, MainActivity.class));
                    return true;
                case R.id.navigation_notifications:
                    return true;
            }
            return false;
        }

    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_notifications);
        listView =(ListView) findViewById(R.id.notificationListView);

        adapter = new CustomAdapter(this, R.layout.notification_card, nameList, actionList, timeList);
        listView.setAdapter(adapter);

        navigation = (BottomNavigationView) findViewById(R.id.navigation_notifications);
        navigation.setOnNavigationItemSelectedListener(mOnNavigationItemSelectedListener);
        navigation.setSelectedItemId(R.id.navigation_notifications);
    }

    public void refresh(){
        Toast.makeText(this, "Refreshing", Toast.LENGTH_SHORT).show();
        listView.setAdapter(adapter);
    }
}

